# -*- coding: utf-8 -*-

"""photos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from . import views


router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'imports', views.ImportViewSet)
router.register(r'photos', views.PhotoViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'photo_exif', views.PhotoExifViewSet)

schema_view = get_swagger_view(title='Photos API')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('settings/', include('usersettings.urls')),

    path('', views.photolist, name='photolist'),
    re_path(r'^photolist/(?P<view>[r,e,i]{1})/$',
            views.photolist, name='photolist'),
    path('detail/<int:photo_id>/', views.detail, name='photodetail'),
    path('new/', views.new, name='new'),
    path('edit/<int:photo_id>/', views.edit, name='photoedit'),
    path('imgedit/<int:photo_id>/', views.imgedit, name='imgedit'),
    path('file-upload', views.fileupload, name='fileupload'),
    path('delete/<int:photo_id>/', views.delete, name='photodelete'),

    path('processdelete/', views.processdelete, name='processdelete'),
    path('processassign/', views.processassign, name='processassign'),
    path('processdownload/', views.processdownload, name='processdownload'),

    path('eventlist/', views.EventListView.as_view(), name='eventlist'),
    path('eventcreate/', views.EventCreateView.as_view(), name='eventcreate'),
    path('eventupdate/<int:pk>/',
         views.EventUpdateView.as_view(), name='eventupdate'),
    path('eventdelete/<int:pk>/',
         views.EventDeleteView.as_view(), name='eventdelete'),

    path('taglist/', views.TagListView.as_view(), name='taglist'),
    path('tagcreate/', views.TagCreateView.as_view(), name='tagcreate'),
    path('tagupdate/<int:pk>/', views.TagUpdateView.as_view(), name='tagupdate'),
    path('tagdelete/<int:pk>/', views.TagDeleteView.as_view(), name='tagdelete'),

    path('photos_as_json/', views.photos_as_json),

    path('photos/', include(router.urls)),
    path('accounts/', include('accounts.urls')),
    path('schema/', schema_view)
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
