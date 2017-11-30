from django.db import models


# Create your models here.
class ImageTb(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    post = models.ForeignKey('PostTb', models.DO_NOTHING, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'image_tb'


class PostTb(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    desertion_id = models.CharField(max_length=255, blank=True, null=True)
    feature = models.CharField(max_length=255, blank=True, null=True)
    gender_type = models.CharField(max_length=255, blank=True, null=True)
    happen_date = models.DateTimeField(blank=True, null=True)
    happen_gungu_code = models.BigIntegerField(blank=True, null=True)
    happen_place = models.CharField(max_length=255, blank=True, null=True)
    happen_sido_code = models.BigIntegerField(blank=True, null=True)
    helper_contact = models.CharField(max_length=255, blank=True, null=True)
    helper_name = models.CharField(max_length=255, blank=True, null=True)
    hit_count = models.BigIntegerField(blank=True, null=True)
    is_display = models.TextField(blank=True, null=True)  # This field type is a guess.
    kind_code = models.BigIntegerField(blank=True, null=True)
    kind_name = models.CharField(max_length=255, blank=True, null=True)
    neuter_type = models.CharField(max_length=255, blank=True, null=True)
    notice_begin_date = models.DateTimeField(blank=True, null=True)
    notice_end_date = models.DateTimeField(blank=True, null=True)
    notice_id = models.CharField(max_length=255, blank=True, null=True)
    post_type = models.CharField(max_length=255, blank=True, null=True)
    shelter_code = models.BigIntegerField(blank=True, null=True)
    shelter_contact = models.CharField(max_length=255, blank=True, null=True)
    shelter_name = models.CharField(max_length=255, blank=True, null=True)
    state_type = models.CharField(max_length=255, blank=True, null=True)
    uid = models.CharField(max_length=255, blank=True, null=True)
    up_kind_code = models.BigIntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'post_tb'


class CommentTb(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    is_display = models.TextField(blank=True, null=True)  # This field type is a guess.
    post = models.ForeignKey('PostTb', models.DO_NOTHING, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment_tb'


class BookmarkTb(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    post_id = models.BigIntegerField(blank=True, null=True)
    user_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bookmark_tb'

class BreedTb(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    kind_code = models.BigIntegerField(unique=True, blank=True, null=True)
    kind_name = models.CharField(max_length=255, blank=True, null=True)
    up_kind_code = models.BigIntegerField(blank=True, null=True)
    up_kind_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'breed_tb'