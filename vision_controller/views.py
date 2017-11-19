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

# vision_request = {
#     'image': None,
#     'features': [{'type': vision.enums.Feature.Type.LABEL_DETECTION},
#                  {'type': vision.enums.Feature.Type.IMAGE_PROPERTIES},
#                  {'type': vision.enums.Feature.Type.SAFE_SEARCH_DETECTION}]
# }

VisionRequest = collections.namedtuple('VisionRequest',['image','features'])
VisionRequest.__new__.__defaults__ = (None,[{'type': vision.enums.Feature.Type.LABEL_DETECTION},
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

ColorResults = collections.namedtuple('ColorResults',['color','score','fraction'])
LabelResults = collections.namedtuple('LabelResults',['label','score'])


def get_vision_result(url):
    image = vision_controller.utils.download_file(url)
    vision_request = VisionRequest(image=types.Image(content=image.read()))
    response = client.annotate_image(vision_request._asdict())
    # import pdb;pdb.set_trace()
    color_results = get_image_color_results(response)
    label_results = get_label_annotation_results(response)
    return [color_results,label_results]


def get_vision_result_by_file(file):
    vision_request = VisionRequest(image=types.Image(content=file.read()))
    response = client.annotate_image(vision_request._asdict())
    color_results = get_image_color_results(response)
    label_results = get_label_annotation_results(response)
    file.seek(0)
    return [color_results,label_results]


def get_image_color_results(res):
    colors = res.image_properties_annotation.dominant_colors.colors
    # protobuf ListValue map 가능 여부 확인 필요
    # color_list = list(map(lambda x:' '.join([x.color.red,x.color.green,x.color.blue]),colors))
    # 임시로 for문 사용
    result = ColorResults(color=list(),score=list(),fraction=list())
    for item in colors:
        x = item.color
        result.color.append(' '.join([str(x.red),str(x.green),str(x.blue)]))
        result.score.append(str(item.score))
        result.fraction.append(str(item.pixel_fraction))
    return result


def get_label_annotation_results(res):
    labels = res.label_annotations
    result = LabelResults(label=list(),score=list())
    for item in labels:
        if filter_labels(item.description):
            result.label.append(item.description)
            result.score.append(str(item.score))
    return result


def filter_labels(label):
    return (label not in filter_list)


def insert_vision_result(color_result, label_result, post_type, url, post_id=-1):
    entity = VisionTb(post_type=post_type,image_url=url,
                      color_rgb=color_result.color,color_score=color_result.score,
                      color_fraction=color_result.fraction,label=label_result.label,
                      label_score=label_result.score, post_id=post_id)
    entity.save()