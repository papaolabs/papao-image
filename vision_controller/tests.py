from django.test import TestCase
from vision_controller import views

# Create your tests here.
class VisionControllerTest(TestCase):
    def test_get_vision_result(self):
        test_url = "http://www.9dog.co.kr/wp-content/uploads/2013/07/img_0114.jpg"
        result = views.get_vision_result(test_url)
        print(result)

