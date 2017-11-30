import ast
import datetime

from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb, BreedTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views

batch_size = 10
batch_target_days = 30

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
    post_entries = PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(days=batch_target_days))\
        .filter(post_type__exact="SYSTEM")\
        .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id"))\
        .values_list("id","up_kind_code","kind_code")
    post_ids = list(map(lambda x:x[0],post_entries))
    entries = ImageTb.objects.filter(
            post_id__in=post_ids).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i,item in enumerate(sliced_list):
        if i % 10 == 0:
            print("[SYSTEM] %d entries complete" % (i*10))
        results = vision_views.get_batch_vision_result(item)
        list(map(lambda x: vision_views.insert_vision_result(color_results=x[0].color_results,
                                                label_results=x[0].label_results,
                                                post_type="SYSTEM", url=x[1], post_id=x[2],
                                                up_kind_code=post_entries[i][1],
                                                kind_code=post_entries[i][2]), results))
    return

def feature_extraction_batch_job_on_etc():
    now = datetime.datetime.now()
    post_entries = PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(days=batch_target_days))\
        .exclude(post_type__exact="SYSTEM")\
        .exclude(id__in=VisionTb.objects.exclude(post_type__exact="SYSTEM").values_list("post_id"))\
        .values_list("id","up_kind_code","kind_code","post_type")
    post_ids = list(map(lambda x:x[0],post_entries))
    entries = ImageTb.objects.filter(
            post_id__in=post_ids).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i,item in enumerate(sliced_list):
        if i % 10 == 0:
            print("[%s] %d entries complete" % (post_entries[i][3],i*10))
        results = vision_views.get_batch_vision_result(item)
        list(map(lambda x: vision_views.insert_vision_result(color_results=x[0].color_results,
                                                label_results=x[0].label_results,
                                                post_type=post_entries[i][3].upper(), url=x[1], post_id=x[2],
                                                up_kind_code=post_entries[i][1],
                                                kind_code=post_entries[i][2]), results))
    return


def sync_batch_job_to_post_tb_with_vision_tb():
    # import pdb;pdb.set_trace()
    now = datetime.datetime.now()
    entries = VisionTb.objects.exclude(post_type__exact="SYSTEM").filter(post_id__exact=-1)
    urls = entries.values_list("image_url")
    post_entries = ImageTb.objects.filter(url__in=urls)


def color_search_batch_job():
    return


def test(request):
    #feature_extraction_batch_job_on_system()
    feature_extraction_batch_job_on_etc()
    now = datetime.datetime.now()
    # vision_views.get_search_result_with_time(120,now-datetime.timedelta(weeks=2),now)
    # get_kind_codes_from_vision_table()
    sync_batch_job_to_post_tb_with_vision_tb()


def get_kind_codes_from_vision_table():
    entries = VisionTb.objects.order_by('kind_code').distinct().values()
    print(len(entries))
    with open("breed.tsv","w") as fp:
        for entry in entries:
            # import pdb;pdb.set_trace()
            up_kind_code = filter_label_annotations(ast.literal_eval(entry['label']),entry['kind_code'],fp)
            if up_kind_code != entry['up_kind_code']:
                print(up_kind_code,entry['label'])
                # import pdb;pdb.set_trace()



def filter_label_annotations(label,kind_code,fp):
    up_kind_code = -1
    kind_name = BreedTb.objects.get(kind_code=kind_code).kind_name
    temp_list = list()
    for item in label:
        if item.find("dog") != -1 and up_kind_code == -1:
            up_kind_code = 417000
        elif item.find("cat") != -1  and up_kind_code == -1:
            up_kind_code = 422400
        if item not in filter_list:
            temp_list.append(item)
    if temp_list:
        fp.write("%s\t%s\t%s\t%s\n" % (kind_name,kind_code,temp_list[0],temp_list))
    return up_kind_code
