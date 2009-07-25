"""
views for albums
"""

from django.views.generic.list_detail import object_list
from netwizard.photogallery.models import Photo, Album

def list(request, **kwargs):
    return object_list(request, paginate_by=50,
            queryset=Album.objects.published(),
            template_name='photogallery/list_albums.html',
            template_object_name='album')

def index(request, **kwargs):
    return list(request, **kwargs)
