from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb
# Create your views here.


def get_image_url_list():
    import pdb;pdb.set_trace()
    entry = ImageTb.objects.get()
    return

def test(request):
    get_image_url_list()