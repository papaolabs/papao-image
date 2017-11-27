from django.test import TestCase
from batch_controller import views
from batch_controller.models import ImageTb, PostTb
# Create your tests here.

class BatchControllerTest(TestCase):
    def setUp(self):
        ImageTb.objects.create(post_id=1, url="http://www.animal.go.kr/files/shelter/2017/11/201711161111684.jpg")

    def test_get_image_url_list(self):
        import pdb;pdb.set_trace()
        views.get_image_url_list()