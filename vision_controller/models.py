from django.db import models

# Create your models here.

class VisionResults(models.Model):
    # 이미지 내의 상위 10개 색에 대한 rgb 값과 score
    color_rgb = models.CharField(max_length=255)
    color_score = models.CharField(max_length=255)
    color_fraction = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    label_score = models.FloatField()