from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
# Create your views here.


def get_image_url_list():
    entry = ImageTb.objects.get()
    return

def test(request):
    get_image_url_list()