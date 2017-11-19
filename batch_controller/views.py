from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
from vision_controller.models import VisionTb

# Create your views here.

def get_shelter_url_list():
    if __name__ == '__main__':
        entries = ImageTb.objects.filter(
            post_id__in=PostTb.objects.filter(post_type__exact="SYSTEM")
                .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id"))
                .values_list("id", flat=True))


    return


def test(request):
    get_shelter_url_list()
