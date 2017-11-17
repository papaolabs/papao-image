from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view
from . import views

schema_view = get_swagger_view(title='Image Storage API')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^swagger-ui.html$',schema_view),
    url(r'^upload$', views.post_image, name='upload'),
    url(r'^download/(?P<filename>\S+)', views.get_image, name='download'),
    url(r'^delete/(?P<filename>\S+)', views.delete_image, name='delete'),
]
