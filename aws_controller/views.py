from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3
import tempfile
import mimetypes
from vision_controller import views as vision_views

bucket_name = 'papao-s3-bucket'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
hostname = "localhost:8000"


def get_image(request, filename):
    f = tempfile.TemporaryFile()
    bucket.download_fileobj(filename, f)
    f.seek(0)
    return HttpResponse(f.read(),content_type=mimetypes.guess_type(filename))


@csrf_exempt
def post_image(request):
    files = request.FILES.getlist('file')
    response = vision_views.get_vision_result_by_file(files[0])
    filenames = list(map(lambda x: upload_image(x), files))
    return JsonResponse({'status': 'OK', 'image_url': list(map(lambda x:hostname+"/v1/download/"+x,filenames))})


def delete_image(request, filename):
    response = bucket.delete_objects(
        Delete={
            'Objects': [
                {
                    'Key': filename
                },
            ]
        }
    )
    return JsonResponse(response)


def index(request):
    return HttpResponse("Hello, world!")


def upload_image(file):
    bucket.upload_fileobj(file, file.name)
    return file.name
