# -*- coding: utf-8 -*-
import json
import os
import zipfile
import io
import requests
import exifread
from shutil import rmtree

from django.conf import settings
from django.apps import apps
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import ListView, UpdateView, CreateView, DeleteView

from photos import parse_exif_data
from photos.models import Photo, Event, Tag, Import
from photos.filters import PhotoFilter
from photos.forms import PhotoForm
from usersettings.models import UserSettings

from rest_framework import viewsets
from .serializers import (PhotoSerializer, EventSerializer, TagSerializer,
                          ImportSerializer, UserSerializer, PhotoEXIFSerializer)


@login_required(login_url='/accounts/login/')
def photolist(request):
    
    viewtype = request.GET.get('viewtype', None)
    
    try:
        settings = UserSettings.objects.get(user=request.user)
        recent = settings.recent
    except UserSettings.DoesNotExist:
        recent = 10

    if viewtype is None:
        photos = PhotoFilter(request.GET, queryset=Photo.objects.all())
    else:
        photos = PhotoFilter(request.GET, queryset=Photo.objects.all().order_by(viewtype))
    
    return render(request, 'photos/photolist.html', {'photos': photos, 'recent': recent, 'view': viewtype})


@login_required(login_url='/accounts/login/')
def detail(request, photo_id):

    google_api_key = getattr(settings, "GEOPOSITION_GOOGLE_MAPS_API_KEY", None)
    photo = Photo.objects.get(pk=photo_id)
    return render(request, 'photos/photodetail.html', {'photo': photo, 'google_api_key': google_api_key})


@login_required(login_url='/accounts/login/')
def new(request):

    return render(request, 'photos/photonew.html', {})


@login_required(login_url='/accounts/login/')
def edit(request, photo_id):

    try:
        photo = Photo.objects.get(pk=photo_id)
    except Photo.DoesNotExist:
        messages.error(request, _(
            'Photo does not exist.'))
        return HttpResponseRedirect(reverse('photolist'))

    if request.method == 'POST':

        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('photolist'))

        form = PhotoForm(request.POST, instance=photo)
        if form.is_valid():
            if 'latitude' in form.changed_data or 'longitude' in form.changed_data:
                form.instance.geocode()
            form.save()
            messages.success(request, _('photo metadata changed.'))
            return HttpResponseRedirect(reverse('photolist'))

    else:
        form = PhotoForm(instance=photo)

    return render(request, 'photos/photoedit.html', {'form': form})


@login_required(login_url='/accounts/login/')
def imgedit(request, photo_id):

    photo = Photo.objects.get(pk=photo_id)
    return render(request, 'photos/imgedit.html', {'photo': photo})


@login_required(login_url='/accounts/login/')
def delete(request, photo_id):

    try:
        photo = Photo.objects.get(pk=photo_id)
    except Photo.DoesNotExist:
        messages.error(request, _(
            'Photo does not exist.'))
        return HttpResponseRedirect(reverse('photolist'))

    if request.method == 'POST':

        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('photolist'))

        photo.delete()
        messages.success(request, _(
            'Photo {photo} deleted.').format(photo=photo.name))
        return HttpResponseRedirect(reverse('photolist'))

    return render(request, 'photos/photodelete.html', {'photo': photo})


@login_required(login_url='/accounts/login/')
def fileupload(request):

    if request.method == 'POST':

        upload = Import.objects.create()

        eventstr = request.POST.get('event')
        if eventstr != '':
            event, ev_created = Event.objects.get_or_create(name=eventstr)
        else:
            event, ev_created = Event.objects.get_or_create(name=upload.name)
        tagstr = request.POST.get('tags')
        if tagstr != '':
            tags = tagstr.split(' ')
        else:
            tags = []

        count = 0
        files = request.FILES
        for f in files:

            imgfile = files[f]

            exif_data = exifread.process_file(imgfile, details=False)
            exif_json = parse_exif_data.get_exif_data_as_json(exif_data)
            exif_tsp = parse_exif_data.get_exif_timestamp(exif_data)
            lat, lon = parse_exif_data.get_exif_location(exif_data)
            if lat is not None and lon is not None:
                lat = '{:3.10}'.format(lat)
                lon = '{:3.10}'.format(lon)

            photo = Photo(
                name=imgfile.name.split('.')[0],
                filename=imgfile.name,
                imagefile=imgfile,
                timestamp=exif_tsp,
                uploaded_by=request.user,
                exif=exif_json,
                latitude=lat,
                longitude=lon,
                upload=upload,
            )
            if event:
                photo.event = event

            photo.geocode()
            photo.save()
            count += 1

            for tagstr in tags:
                tag, created = Tag.objects.get_or_create(name=tagstr)
                photo.tags.add(tag)

        messages.success(request, _(
            'successfully added {count} photos.').format(count=count))

        return HttpResponse('ok')

@login_required(login_url='/accounts/login/')
def geocode(request):
    photos = Photo.objects.all()
    count = 0
    for photo in photos:
        if photo.latitude and photo.longitude:
            # address = dict()
            # geoCoder = MapsGeocoder(geocoder=Nominatim())
            # location = geoCoder.getAddressFromGeocode(photo.latitude, photo.longitude)
            # if location is not None:
            #     if len(location) > 0:
            #         loc_str = location.raw['display_name']
            #         address = {'formatted': loc_str, 'address': location.raw}
            #         photo.address = address
            photo.geocode()
            photo.save()
            count += 1
    messages.success(request, _(
        'successfully geocoded {count} photos.').format(count=count))
    return HttpResponseRedirect(reverse('photolist'))


@login_required(login_url='/accounts/login/')
def processdelete(request):
    ids = request.POST.getlist('ids[]')
    delete = Photo.objects.filter(pk__in=ids)
    delete.delete()
    return HttpResponse('success')


@login_required(login_url='/accounts/login/')
def delete_empty(request):

    usedUploads = Photo.objects.all().order_by('upload_id').values('upload_id').distinct('upload_id')
    uploadsToDelete = Import.objects.exclude(pk__in=usedUploads)
    for upload in uploadsToDelete:
        dirname = os.path.abspath('{}/photos/{}'.format(settings.MEDIA_ROOT, upload.slug))
        try:
            rmtree(dirname)
        except:
            import traceback
            traceback.print_exc()
            messages.error(request, _('could not remove directory'))
    uploadsToDelete.delete()

    usedEvents = Photo.objects.all().order_by('event_id').values('event_id').distinct('event_id')
    Event.objects.exclude(pk__in=usedEvents).delete()

    return HttpResponseRedirect(reverse('photolist'))



@login_required(login_url='/accounts/login/')
def processassign(request):
    ids = request.POST.getlist('ids[]')
    evt = request.POST.get('event')
    tgs = request.POST.getlist('tags[]')

    if evt:
        event = Event.objects.get(pk=evt)
    else:
        event = None
    tags = Tag.objects.filter(pk__in=tgs)
    photos = Photo.objects.filter(pk__in=ids)

    with transaction.atomic():
        for photo in photos:
            if event is not None:
                photo.event = event
            photo.tags.add(*tags)
            photo.save()

    return HttpResponse('success')


@login_required(login_url='/accounts/login/')
def processdownload(request):
    ids = request.POST.getlist('ids[]')
    filenames = [photo.imagefile.path for photo in Photo.objects.filter(pk__in=ids)]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "fotos"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(content_type="application/force-download")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    resp.write(s.getvalue())

    return resp


class EventListView(ListView):

    model = Event
    # paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eventlist'] = Event.objects.all()
        return context


class EventUpdateView(UpdateView):

    model = Event
    fields = ['name', ]
    template_name = 'photos/event_form.html'
    success_url = reverse_lazy('eventlist')


class EventCreateView(CreateView):

    model = Event
    fields = ['name', ]
    template_name = 'photos/event_form.html'
    success_url = reverse_lazy('eventlist')


class EventDeleteView(DeleteView):

    model = Event
    success_url = reverse_lazy('eventlist')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            messages.info(request, _('Delete cancelled'))
            return HttpResponseRedirect(reverse('eventlist'))
        messages.info(request, _('Event deleted'))
        return super(EventDeleteView, self).post(request, *args, **kwargs)


class TagListView(ListView):

    model = Tag
    # paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taglist'] = Tag.objects.all()
        return context


class TagUpdateView(UpdateView):

    model = Tag
    fields = ['name', ]
    template_name = 'photos/tag_form.html'
    success_url = reverse_lazy('taglist')


class TagCreateView(CreateView):

    model = Tag
    fields = ['name', ]
    template_name = 'photos/tag_form.html'
    success_url = reverse_lazy('taglist')


class TagDeleteView(DeleteView):

    model = Tag
    success_url = reverse_lazy('taglist')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            messages.info(request, _('Delete cancelled'))
            return HttpResponseRedirect(reverse('taglist'))
        messages.info(request, _('Tag deleted'))
        return super(TagDeleteView, self).post(request, *args, **kwargs)

def photos_as_json(request):
    photos = Photo.objects.all().values('id', 'name')
    return JsonResponse({'results': list(photos)})


# REST Views
class PhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Photos.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ImportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Imports.
    """
    queryset = Import.objects.all()
    serializer_class = ImportSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PhotoExifViewSet(viewsets.ModelViewSet):
    """
    API endpoint for EXIF-Data.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoEXIFSerializer
