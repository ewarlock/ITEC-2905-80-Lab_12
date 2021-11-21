# urls for our app - distinct from urls for project
from django.urls import path
# path describes a url and the relationship between url text and code response
from . import views # import views from this directory

urlpatterns = [
    path('', views.home, name='home'), # call home function in views.py
    path('add', views.add, name='add_video'),
    path('video_list', views.video_list, name='video_list'), # but avoid using list in names
    path('video_detail/<int:video_pk>', views.video_detail, name='video_detail')
]