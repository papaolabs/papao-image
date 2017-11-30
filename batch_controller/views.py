import ast
import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb, BreedTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views

batch_size = 10
batch_target_days = 30

push_url = "http://220.230.124.9:9040/api/v1/push/send"

filter_list = ["dog",
               "dorgi",
               "paw",
               "fur",
               "snout",
               "puppy",
               "kennel",
               "carnivoran",
               "companion",
               "companion dog",
               "dog crate",
               "dog breed",
               "dog like mammal",
               "dog crossbreeds",
               "dog breed group",
               "cat like mammal",
               "mammal",
               "vertebrate",
               "animal shelter"]


def feature_extraction_batch_job_on_system():
    now = datetime.datetime.now()
    post_entries = PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(days=batch_target_days)) \
        .filter(post_type__exact="SYSTEM") \
        .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id")) \
        .values_list("id", "up_kind_code", "kind_code", "happen_date")
    post_ids = list(map(lambda x: x[0], post_entries))
    entries = ImageTb.objects.filter(
        post_id__in=post_ids).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i, item in enumerate(sliced_list):
        if i % 10 == 0:
            print("[SYSTEM] %d entries complete" % (i * 10))
        results = vision_views.get_batch_vision_result(item)
        for j, result in enumerate(results):
            index = (i + 1) * j
            vision_views.insert_vision_result(color_results=result[0].color_results,
                                              label_results=result[0].label_results,
                                              post_type="SYSTEM", url=result[1], post_id=result[2],
                                              up_kind_code=post_entries[index][1],
                                              kind_code=post_entries[index][2],
                                              happen_date=post_entries[index][3])
    print("feature extraction batch job done.")
    return


def feature_extraction_batch_job_on_etc():
    now = datetime.datetime.now()
    post_entries = PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(days=batch_target_days)) \
        .exclude(post_type__exact="SYSTEM") \
        .exclude(id__in=VisionTb.objects.exclude(post_type__exact="SYSTEM").values_list("post_id")) \
        .values_list("id", "up_kind_code", "kind_code", "post_type", "uid", "helper_name", "happen_date")
    post_ids = list(map(lambda x: x[0], post_entries))
    entries = ImageTb.objects.filter(
        post_id__in=post_ids).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i, item in enumerate(sliced_list):
        if i % 10 == 0:
            print("[%s] %d entries complete" % (post_entries[i][3], i * 10))
        results = vision_views.get_batch_vision_result(item)
        for j, result in enumerate(results):
            index = (i + 1) * j
            vision_views.insert_vision_result(color_results=result[0].color_results,
                                              label_results=result[0].label_results,
                                              post_type=post_entries[index][3].upper(), url=result[1],
                                              post_id=result[2],
                                              up_kind_code=post_entries[index][1],
                                              kind_code=post_entries[index][2])
            if post_entries[index][3] == "MISSING":
                find_search_push_candidate_batch_job([{"id": post_entries[index][0],
                                                       "uid": post_entries[index][4],
                                                       "helper_name": post_entries[index][5],
                                                       "happen_date": post_entries[index][6]}])

    print("feature extraction batch job done.")
    return


def sync_batch_job_to_post_tb_with_vision_tb():
    try:
        now = datetime.datetime.now()
        entries = VisionTb.objects.exclude(post_type__exact="SYSTEM").filter(post_id__exact=-1)

        for item in entries:
            url = item.image_url
            image_entry = ImageTb.objects.filter(url__exact=url).values_list("post_id", flat=True)
            if len(image_entry):
                post_entry = PostTb.objects.filter(id__exact=image_entry)
                kind_code_entry = post_entry.values("id", "up_kind_code", "kind_code")[0]
                push_entry = post_entry.filter(post_type__exact="MISSING").values("id", "uid", "helper_name",
                                                                                  "happen_date")
                item.post_id = kind_code_entry["id"]
                item.up_kind_code = kind_code_entry['up_kind_code']
                item.kind_code = kind_code_entry["kind_code"]
                item.modified_date = now
                item.save()
                find_search_push_candidate_batch_job(push_entry)
            else:
                item.delete()
        print("sync batch job done.")
    except Exception as err:
        print("Sync error %s" % str(err))


def find_search_push_candidate_batch_job(entries=None):
    now = datetime.datetime.now()
    if entries == None:
        entries = PostTb.objects.filter(post_type__exact="MISSING") \
            .values("id", "uid", "helper_name", "happen_date")
        # .fliter(happen_date__gte=now-)
    for item in entries:
        try:
            result_posts, return_urls = vision_views.get_search_result_with_time(post_id=item['id'],
                                                                                 start_date=item['happen_date'],
                                                                                 end_date=now
                                                                                 )
            if len(result_posts) > 1:
                send_push_message(post_id=item['id'], uid=item['uid'], user_name=item['helper_name'])
        except Exception as err:
            # import pdb;pdb.set_trace()
            print("Push Error : %s" % str(err))
            continue

    print("push batch job done.")
    return


def send_push_message(post_id, uid, user_name):
    try:
        header = {'Content-Type': 'application/json'}
        r = requests.post(push_url + "?postId=" + str(post_id), headers=header,
                          json={
                              "message": "%s님의 실종동물과 유사한 동물이 등록되었습니다" % user_name,
                              "type": "SEARCH",
                              "userId": str(uid)
                          })
    except Exception as err:
        print("ERROR : 푸시 발송 실패 %s" % str(err))


def test(request):
    # import pdb;
    # pdb.set_trace()
    # feature_extraction_batch_job_on_system()
    # feature_extraction_batch_job_on_etc()
    now = datetime.datetime.now()
    # vision_views.get_search_result_with_time(120,now-datetime.timedelta(weeks=2),now)
    # get_kind_codes_from_vision_table()

    # sync_batch_job_to_post_tb_with_vision_tb()
    find_search_push_candidate_batch_job()
    return


def get_kind_codes_from_vision_table():
    entries = VisionTb.objects.order_by('kind_code').distinct().values()
    print(len(entries))
    with open("breed.tsv", "w") as fp:
        for entry in entries:
            # import pdb;pdb.set_trace()
            up_kind_code = filter_label_annotations(ast.literal_eval(entry['label']), entry['kind_code'], fp)
            if up_kind_code != entry['up_kind_code']:
                print(up_kind_code, entry['label'])
                # import pdb;pdb.set_trace()


def filter_label_annotations(label, kind_code, fp):
    up_kind_code = -1
    kind_name = BreedTb.objects.get(kind_code=kind_code).kind_name
    temp_list = list()
    for item in label:
        if item.find("dog") != -1 and up_kind_code == -1:
            up_kind_code = 417000
        elif item.find("cat") != -1 and up_kind_code == -1:
            up_kind_code = 422400
        if item not in filter_list:
            temp_list.append(item)
    if temp_list:
        fp.write("%s\t%s\t%s\t%s\n" % (kind_name, kind_code, temp_list[0], temp_list))
    return up_kind_code


def feature_extraction():
    sync_batch_job_to_post_tb_with_vision_tb()
    feature_extraction_batch_job_on_system()
    feature_extraction_batch_job_on_etc()
    return


def batch_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(feature_extraction, 'interval', minutes=10)
    scheduler.add_job(find_search_push_candidate_batch_job, 'cron', hour=14)
    scheduler.start()
    print("Batch start")


batch_scheduler()
