from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload$',views.postImage, name='upload'),
    url(r'^download/(?P<filename>\S+)',views.getImage, name='download'),
    url(r'^delete/(?P<filename>\S+)',views.deleteImage, name='delete')
]
