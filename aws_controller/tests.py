from django.test import TestCase
import tempfile
from vision_controller.utils import download_file
from aws_controller import views
import urllib3
import requests

test_images = ['http://www.animal.go.kr/files/shelter/2017/11/201711151511277.jpg',
               'http://www.animal.go.kr/files/shelter/2017/11/201711151311784.jpg',
               'http://www.animal.go.kr/files/shelter/2017/11/201711151811733.jpg']

hostname = 'http://localhost:8000'


class AwsControllerTest(TestCase):
    def test_post_images(self):
        test_list = list(map(lambda x: download_file(x), test_images))
        import pdb;
        pdb.set_trace()
        req = requests.post(url=hostname + '/v1/upload',
                            files=[('file', ("test_1.jpg", test_list[0].read())),
                                   ('file', ("test_2.jpg", test_list[1].read())),
                                   ('file', ("test_3.jpg", test_list[2].read()))])
