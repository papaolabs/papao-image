from django.db import models

class Image(models.Model):
    user_key = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)
