import collections
import os
from django.shortcuts import render
from google.cloud import vision
from google.cloud.vision import types
import json
import vision_controller.utils
from vision_controller.models import VisionTb

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

filter_list = ["dog",
               "dorgi",
               "paw",
               "fur",
               "snout",
               "puppy",
               "kennel",
               "carnivoran",
               "companion",
               "companion dog",
               "dog crate",
               "dog breed",
               "dog like mammal",
               "dog crossbreeds",
               "dog breed group",
               "cat like mammal",
               "mammal",
               "vertebrate",
               "animal shelter"]

ColorResults = collections.namedtuple('ColorResults', ['color', 'score', 'fraction'])
LabelResults = collections.namedtuple('LabelResults', ['label', 'score'])
VisionResults = collections.namedtuple('VisionResults', ['label_results', 'color_results'])


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
    urls = list(map(lambda x:x[0],entries))
    post_ids = list(map(lambda x:x[1],entries))
    images = vision_controller.utils.download_files(urls)
    vision_requests = list(map(lambda x: VisionRequest(image=types.Image(content=x.read()))._asdict(), images))
    response = client.batch_annotate_images(vision_requests)
    results = list(map(lambda x: encode_vision_results(x), response.responses))
    results = list(zip(results,urls, post_ids))
    list(map(lambda x: insert_vision_result(color_results=x[0].color_results,
                                           label_results=x[0].label_results,
                                            post_type="SYSTEM",url=x[1], post_id=x[2]), results))



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
        if filter_labels(item.description):
            result.label.append(item.description)
            result.score.append(str(item.score))
    return result


def filter_labels(label):
    return (label not in filter_list)


def insert_vision_result(color_results,label_results, post_type, url, post_id=-1):
    entity = VisionTb(post_type=post_type, image_url=url,
                      color_rgb=color_results.color, color_score=color_results.score,
                      color_fraction=color_results.fraction, label=label_results.label,
                      label_score=label_results.score, post_id=post_id)
    entity.save()
