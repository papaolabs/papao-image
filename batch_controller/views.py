from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views


# Create your views here.

def get_shelter_url_list():
    entries = ImageTb.objects.filter(
        post_id__in=PostTb.objects.filter(post_type__exact="SYSTEM")
            .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id"))
            .values_list("id", flat=True))[:10].values_list("url", "post_id")

    import pdb;
    pdb.set_trace()
    vision_views.get_batch_vision_result(list(entries))
    return


def test(request):
    get_shelter_url_list()
