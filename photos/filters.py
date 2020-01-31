import django_filters
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Photo, Event, Tag


class PhotoFilter(django_filters.FilterSet):
    class Meta:
        model = Photo
        fields = [
            'event', 'tags', 'timestamp',
            'uploaded', 'uploaded_by', 'upload'
        ]

    event = django_filters.ModelChoiceFilter(
        queryset=Event.objects.all(),
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
    )
    timestamp = django_filters.DateFromToRangeFilter()
    uploaded = django_filters.DateFromToRangeFilter()
    uploaded_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PhotoFilter, self).__init__(*args, **kwargs)
        visibles = Photo.objects.filter(
            Q(owner=user) |
            Q(shared=user)
        )
        # Filtering events doesn't allow assign photo to empty event!
        # self.filters['event'].queryset = Event.objects.filter(
        #     photo__pk__in=visibles
        # ).distinct()
    