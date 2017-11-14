from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3
import tempfile
import mimetypes

bucket_name = 'papao-s3-bucket'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
hostname = "localhost:8000"


def getImage(request,filename):
    f = tempfile.TemporaryFile()
    bucket.download_fileobj(filename, f)
    f.seek(0)
    return HttpResponse(f.read(),content_type=mimetypes.guess_type(filename))


@csrf_exempt
def postImage(request):
    files = request.FILES.getlist('file')
    filenames = list(map(lambda x: uploadImage(x), files))
    return JsonResponse({'status': 'OK', 'image_url': list(map(lambda x:hostname+"/v1/download/"+x,filenames))})

def deleteImage(request,filename):
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


def uploadImage(file):
    bucket.upload_fileobj(file, file.name)
    return file.name
