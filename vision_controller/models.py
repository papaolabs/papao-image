from django.db import models

# Create your models here.

class VisionTb(models.Model):
    # 이미지 내의 상위 10개 색에 대한 rgb 값과 score
    id = models.BigAutoField(primary_key=True)
    post_type = models.CharField(max_length=10)
    image_url = models.CharField(max_length=255)
    color_rgb = models.CharField(max_length=255)
    color_score = models.CharField(max_length=255)
    color_fraction = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    label_score = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now_add=True, blank=True)
    class Meta:
        managed = True
        db_table = 'vision_tb'