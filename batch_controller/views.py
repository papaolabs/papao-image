import ast
import datetime

from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views

batch_size = 10
batch_target_weeks = 10

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


def feature_extraction_batch_job():
    now = datetime.datetime.now()
    entries = ImageTb.objects.filter(
        post_id__in=PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(weeks=batch_target_weeks))
            .filter(post_type__exact="SYSTEM")
            .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id"))
            .values_list("id", flat=True)).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i,item in enumerate(sliced_list):
        if i % 10 == 0:
            print("%d entries complete" % (i*10))
        vision_views.get_batch_vision_result(item)
    return



def test(request):
    # feature_extraction_batch_job()
    now = datetime.datetime.now()
    # vision_views.get_search_result_with_time(120,now-datetime.timedelta(weeks=2),now)
    get_kind_codes_from_vision_table()


def get_kind_codes_from_vision_table():
    entries = VisionTb.objects.all().values()
    # import pdb;pdb.set_trace()
    for entry in entries:
        up_kind_code, kind_code = filter_label_annotations(ast.literal_eval(entry['label']))
        if up_kind_code != entry['up_kind_code']:
            print(entry['label'])



def filter_label_annotations(label):
    up_kind_code = -1
    kind_code = -1
    for item in label:
        if "dog" in item and up_kind_code == -1:
            up_kind_code = 417000
        elif "cat" in item and up_kind_code == -1:
            up_kind_code = 422400
    return up_kind_code, kind_code