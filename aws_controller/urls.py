from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view
from . import views

schema_view = get_swagger_view(title='Image Storage API')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^swagger-ui.html$',schema_view),
    url(r'^upload$', views.post_image, name='upload'),
    url(r'^upload/street$', views.post_image_from_street, name='upload_with_vision'),
    url(r'^download/(?P<filename>\S+)', views.get_image, name='download'),
    url(r'^delete/(?P<filename>\S+)', views.delete_image, name='delete'),
    url(r'^search/(?P<post_id>\S+)$',views.search_image,name='search'),
    url(r'^search_test/(?P<post_id>\S+)$',views.test_search_image,name='search')
]
