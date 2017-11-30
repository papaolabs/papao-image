import collections
import os
from functools import reduce
from operator import itemgetter
import datetime
import time
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.db.models import Q
from google.cloud import vision
from google.cloud.vision import types
import json
import colorsys
import vision_controller.utils
from vision_controller.models import VisionTb
from batch_controller.models import PostTb
import numpy as np
import ast
import csv

try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError:
    print("google credential load fail")
    raise

client = vision.ImageAnnotatorClient()

VisionRequest = collections.namedtuple('VisionRequest', ['image', 'features'])
VisionRequest.__new__.__defaults__ = (None, [{'type': vision.enums.Feature.Type.LABEL_DETECTION},
                                             {'type': vision.enums.Feature.Type.IMAGE_PROPERTIES},
                                             {'type': vision.enums.Feature.Type.SAFE_SEARCH_DETECTION}])

ColorResults = collections.namedtuple('ColorResults', ['color', 'score', 'fraction'])
LabelResults = collections.namedtuple('LabelResults', ['label', 'score'])
VisionResults = collections.namedtuple('VisionResults', ['label_results', 'color_results'])

def init_kind_code_dict():
    temp_dict = {}
    with open('mapping_table.csv','r') as infile:
        reader = csv.reader(infile)
        temp_dict = {rows[0]:int(rows[1]) for rows in reader}
    return temp_dict
kind_code_dict = init_kind_code_dict()


def get_vision_result_by_url(url):
    image = vision_controller.utils.download_file(url)
    vision_request = VisionRequest(image=types.Image(content=image.read()))
    response = client.annotate_image(vision_request._asdict())
    color_results = get_image_color_results(response)
    label_results = get_label_annotation_results(response)
    return VisionResults(color_results=color_results, label_results=label_results)


def get_vision_result_by_file(file):
    vision_request = VisionRequest(image=types.Image(content=file.read()))
    response = client.annotate_image(vision_request._asdict())
    file.seek(0)
    return encode_vision_results(response)


def get_batch_vision_result(entries):
    urls = list(map(lambda x: x[0], entries))
    post_ids = list(map(lambda x: x[1], entries))
    images = vision_controller.utils.download_files(urls)
    vision_requests = list(map(lambda x: VisionRequest(image=types.Image(content=x.read()))._asdict(), images))
    response = client.batch_annotate_images(vision_requests)
    results = list(map(lambda x: encode_vision_results(x), response.responses))
    results = list(zip(results, urls, post_ids))
    return results


def encode_vision_results(res):
    color_results = get_image_color_results(res)
    label_results = get_label_annotation_results(res)
    return VisionResults(color_results=color_results, label_results=label_results)


def get_image_color_results(res):
    colors = res.image_properties_annotation.dominant_colors.colors
    # protobuf ListValue map 가능 여부 확인 필요
    # color_list = list(map(lambda x:' '.join([x.color.red,x.color.green,x.color.blue]),colors))
    # 임시로 for문 사용
    result = ColorResults(color=list(), score=list(), fraction=list())
    for item in colors:
        x = item.color
        result.color.append(' '.join([str(x.red), str(x.green), str(x.blue)]))
        result.score.append(str(item.score))
        result.fraction.append(str(item.pixel_fraction))
    return result


def get_label_annotation_results(res):
    labels = res.label_annotations
    result = LabelResults(label=list(), score=list())
    for item in labels:
        result.label.append(item.description)
        result.score.append(str(item.score))
    return result


def get_search_result_with_time(post_id, start_date, end_date):
    query = VisionTb.objects.get(post_id__exact=post_id)
    query_np = get_hsv_from_rgb(query)
    # double list comprehension 이용하여 rgb -> hsv 변환 후 distance measure
    candidate = VisionTb.objects.filter(up_kind_code__exact=query.up_kind_code) \
        .filter(kind_code__exact=query.kind_code) \
        .filter(happen_date__gte=query.happen_date)\
        .filter(happen_date__lte=end_date)\
        .exclude(post_type__exact="MISSING")\
        .exclude(color_rgb__exact="[]")
    cand_id_url = candidate.values_list("post_id","image_url")
    candidate = candidate.values()
    cand_np = np.asarray(list(map(lambda x: get_hsv_from_rgb(x), candidate)))
    distance = get_hsv_distance(query_np, cand_np)
    # color_ratio = np.asarray(list(map(lambda x:float(x),ast.literal_eval(query.color_fraction))))
    color_score = np.asarray(list(map(lambda x: float(x), ast.literal_eval(query.color_score)[:5])))
    result_distance = np.sum(distance * (color_score), axis=1).tolist()
    sorted_index = sorted(range(len(result_distance)), key=lambda k: result_distance[k])
    cand_id = list(map(lambda x:x[0],cand_id_url))
    # post = PostTb.objects.filter(reduce(lambda x, y: x | y, [Q(id=id) for id in cand_id])).values()
    post = [PostTb.objects.get(id__exact=id) for id in cand_id]
    # import pdb;pdb.set_trace()
    sorted_post = itemgetter(*sorted_index)(post)
    sorted_url = itemgetter(*sorted_index)(list(map(lambda x:x[1],cand_id_url)))
    return sorted_post,sorted_url


def insert_vision_result(color_results, label_results, post_type, url, post_id=-1, up_kind_code=-1, kind_code=-1,happen_date=datetime.datetime.now()):
    entity = VisionTb(post_type=post_type, image_url=url,
                      color_rgb=color_results.color, color_score=color_results.score,
                      color_fraction=color_results.fraction, label=label_results.label,
                      label_score=label_results.score, post_id=post_id,
                      up_kind_code=up_kind_code, kind_code=kind_code, happen_date=happen_date)
    entity.save()

def get_kind_type_codes(label_list):
    up_kind_code = -1
    kind_code = -1
    for item in label_list:
        if up_kind_code == -1:
            if item.find("dog") != -1:
                up_kind_code = 417000
            elif item.find("cat") != -1:
                up_kind_code = 422400
        if kind_code == -1:
            kind_code = kind_code_dict.get(item,-1)
    return up_kind_code, kind_code


def get_hsv_from_rgb(image):
    if isinstance(image, VisionTb):
        image = model_to_dict(image)
    color_list = ast.literal_eval(image['color_rgb'])[:5]
    color_list = [item.split() for item in color_list]
    color_list = [list(map(lambda x: float(x), rgb_values)) for rgb_values in color_list]
    return np.asarray([colorsys.rgb_to_hsv(*rgb_values) for rgb_values in color_list])


def get_hsv_distance(query_np, cand_np):
    # import pdb;pdb.set_trace()
    dh = np.minimum(abs(cand_np[:, :, 0] - query_np[None, :, 0]),
                        360 - abs(cand_np[:, :, 0] - query_np[None, :, 0])) / 180.0
    ds = abs(cand_np[:, :, 1] - query_np[None, :, 1])
    dv = abs(cand_np[:, :, 2] - query_np[None, :, 2]) / 255.0
    return np.sqrt(dh * dh + ds * ds + dv * dv)
