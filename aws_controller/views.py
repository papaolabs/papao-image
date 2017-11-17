from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3
import tempfile
import mimetypes
import uuid
from vision_controller import views as vision_views



bucket_name = 'papao-s3-bucket'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
hostname = "220.230.121.76:8000"
# hostname = "localhost:8000"

def get_image(request, filename):
    f = tempfile.TemporaryFile()
    bucket.download_fileobj(filename, f)
    f.seek(0)
    return HttpResponse(f.read(),content_type=mimetypes.guess_type(filename))


@csrf_exempt
def post_image(request):
    try:
        files = request.FILES.getlist('file')
        post_type = request.POST['post_type']
        response = vision_views.get_vision_result_by_file(files[0])
        # !!FIXIT!! : result filtering 하여 축종과 품종을 추출해야 함.
        race_type = '진돗개'
        animal_type = '개'
        filenames = list(map(lambda x: upload_image(x), files))
        vision_views.insert_vision_result(response[0],response[1],post_type=post_type,url=hostname+"/v1/download/"+filenames[0])
        return JsonResponse({'status': 'OK', 'image_url': list(map(lambda x:hostname+"/v1/download/"+x,filenames)),
                             'race_type':race_type, 'animal_type':animal_type})
    except Exception as e:
        return JsonResponse({'status':'Failure',"message":str(e)})



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
    filename = ".".join([uuid.uuid4().hex,file.name.split(".")[-1]])
    bucket.upload_fileobj(file,filename)
    return filename


