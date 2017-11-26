import ast
import datetime

from django.shortcuts import render

from batch_controller.models import ImageTb, PostTb, BreedTb
from vision_controller.models import VisionTb
from vision_controller import views as vision_views

batch_size = 10
batch_target_weeks = 10

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

mapping_dict = {
    "maltese" : "말티즈"
}


def feature_extraction_batch_job():
    now = datetime.datetime.now()
    entries = ImageTb.objects.filter(
        post_id__in=PostTb.objects.filter(happen_date__gte=now - datetime.timedelta(weeks=batch_target_weeks))
            .filter(post_type__exact="SYSTEM")
            .exclude(id__in=VisionTb.objects.filter(post_type__exact="SYSTEM").values_list("post_id"))
            .values_list("id", flat=True)).values_list("url", "post_id")
    entry_list = list(entries)
    sliced_list = [entry_list[i:i + batch_size] for i in range(0, len(entry_list), batch_size)]
    for i,item in enumerate(sliced_list):
        if i % 10 == 0:
            print("%d entries complete" % (i*10))
        vision_views.get_batch_vision_result(item)
    return



def test(request):
    # feature_extraction_batch_job()
    now = datetime.datetime.now()
    # vision_views.get_search_result_with_time(120,now-datetime.timedelta(weeks=2),now)
    get_kind_codes_from_vision_table()


def get_kind_codes_from_vision_table():
    entries = VisionTb.objects.order_by('kind_code').distinct().values()
    print(len(entries))
    with open("breed.tsv","w") as fp:
        for entry in entries:
            # import pdb;pdb.set_trace()
            up_kind_code = filter_label_annotations(ast.literal_eval(entry['label']),entry['kind_code'],fp)
            if up_kind_code != entry['up_kind_code']:
                print(up_kind_code,entry['label'])
                import pdb;pdb.set_trace()



def filter_label_annotations(label,kind_code,fp):
    up_kind_code = -1
    kind_name = BreedTb.objects.get(kind_code=kind_code).kind_name
    temp_list = list()
    for item in label:
        if "dog" in item and up_kind_code == -1:
            up_kind_code = 417000
        elif "cat" in item and up_kind_code == -1:
            up_kind_code = 422400
        if item not in filter_list:
            temp_list.append(item)
    # fp.write("%s\t%s\n" % (kind_name,temp_list))
    return up_kind_code