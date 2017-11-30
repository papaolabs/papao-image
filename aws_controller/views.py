import datetime
import time
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import boto3
import tempfile
import mimetypes
import uuid
from django.forms.models import model_to_dict
from batch_controller.models import CommentTb, BookmarkTb
from vision_controller import views as vision_views
from vision_controller.models import VisionTb

bucket_name = 'papao-s3-bucket'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)
hostname = "http://220.230.121.76:8000"


# hostname = "localhost:8000"

def get_image(request, filename):
    f = tempfile.TemporaryFile()
    bucket.download_fileobj(filename, f)
    f.seek(0)
    return HttpResponse(f.read(), content_type=mimetypes.guess_type(filename))


@csrf_exempt
def post_image_from_street(request):
    try:
        files = request.FILES.getlist('file')
        post_type = request.POST['post_type']
        response = vision_views.get_vision_result_by_file(files[0])
        up_kind_code, kind_code = vision_views.get_kind_type_codes(response.label_results.label)
        filenames = list(map(lambda x: upload_image(x), files))
        vision_views.insert_vision_result(color_results=response.color_results, label_results=response.label_results,
                                          post_type=post_type.upper(), url=hostname + "/v1/download/" + filenames[0])
        return JsonResponse(
            {'status': 'OK', 'image_url': list(map(lambda x: hostname + "/v1/download/" + x, filenames)),
             'kind_code': kind_code, 'up_kind_code': up_kind_code})
    except Exception as e:
        return JsonResponse({'status': 'Failure', "message": str(e)})


@csrf_exempt
def post_image(request):
    try:
        files = request.FILES.getlist('file')
        filenames = list(map(lambda x: upload_image(x), files))
        return JsonResponse(
            {'status': 'OK', 'image_url': list(map(lambda x: hostname + "/v1/download/" + x, filenames))})
    except Exception as e:
        return JsonResponse({'status': 'Failure', "message": str(e)})


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
    VisionTb.objects.filter(image_url__endswith=filename).delete()
    return JsonResponse(response)


@csrf_exempt
def search_image(request, post_id):
    try:
        now = datetime.datetime.now()
        ts = time.time()
        result_post, result_url = vision_views.get_search_result_with_time(post_id=post_id,
                                                                           start_date=now - datetime.timedelta(weeks=4),
                                                                           end_date=now)
        temp_list = list()
        for i, item in enumerate(result_post):
            temp = encode_post_to_result(item)
            temp['imageUrls'] = [
                {
                    "key": 0,
                    "url": result_url[i]
                }
            ]
            temp['bookmarkCount'] = BookmarkTb.objects.filter(post_id__exact=item.id).count()
            temp['commentCount'] = CommentTb.objects.filter(post_id__exact=item.id).count()
            temp_list.append(temp)
        return JsonResponse({'currentPage': 0,
                             "totalElements": 0,
                             "totalPages": 0,
                             "status":"OK",
                             "elements": temp_list})
    except Exception as err:
        print("Search Error : %s" % str(err))
        return JsonResponse({'currentPage': 0,
                             "totalElements": 0,
                             "totalPages": 0,
                             "elements": [],
                             'status':'fail'})



@csrf_exempt
def test_search_image(request, post_id):
    now = datetime.datetime.now()
    result_post, result_url = vision_views.get_search_result_with_time(post_id=post_id,
                                                                       start_date=now - datetime.timedelta(weeks=4),
                                                                       end_date=now)
    return HttpResponse("\n".join(list(map(lambda x:"<img src=%s width=\"200px\" height=\"200px\">"%x,result_url))))


def index(request):
    return HttpResponse("Hello, world!")


def upload_image(file):
    filename = ".".join([uuid.uuid4().hex, file.name.split(".")[-1]])
    bucket.upload_fileobj(file, filename)
    return filename

def encode_post_to_result(item):
    return {"id":item.id,"createdDate":item.created_date,'updatedDate': item.updated_date,
            "genderType":item.gender_type, "happenDate":item.happen_date, "happenPlace":item.happen_place,
            "kindName":item.kind_name, "postType":item.post_type,"hitCount":item.hit_count,
            "stateType":item.state_type}
