import datetime

from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views

batch_size = 10
batch_target_weeks = 10


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
    vision_views.get_search_result_with_time(120,now-datetime.timedelta(weeks=2),now)