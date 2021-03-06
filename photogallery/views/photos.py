import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_page
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, redirect
from tagging.views import tagged_object_list
from tagging.models import TaggedItem
from django.db.models.query import Q

from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object, create_object
from django.template import RequestContext

from photogallery.models import Photo, Album
from photogallery import forms, auth
import re


def list(request, id=None, album_slug=None, template_name=None, paginate_by=None, queryset=None, extra_context=None, **kwargs):
    photos = queryset if queryset is not None else Photo.objects
    if photos:
        photos = photos.published()
    album = None
    if id: # album
        photos = photos.filter(album=id)
        album = Album.objects.published().get(id=id)
    elif album_slug:
        photos = photos.filter(album__slug=album_slug)
        album = Album.objects.published().get(slug=album_slug)

    extra_context = extra_context or {}
    extra_context.update({
        'album': album,
        'last_updated_at': Photo.objects.get_max_updated_at(photos),
        'tag': None,
        })

    return object_list(request, paginate_by=paginate_by or 25,
            queryset=photos, template_name=template_name or 'photogallery/list.html',
            extra_context=extra_context, template_object_name='photo')


def list_tagged(request, tag, template_name=None, extra_context=None, paginate_by=None, **kwargs):
    photos = Photo.objects.published()
    ctx = extra_context or {}
    ctx.update({
        'last_updated_at': Photo.objects.get_max_updated_at(photos),
        'tag': tag,
        })
    return tagged_object_list(request, tag=tag, paginate_by=paginate_by or 25,
            queryset_or_model=photos, template_name=template_name or 'photogallery/list.html',
            extra_context=ctx, template_object_name='photo', **kwargs)


def detail(request, id=None, photo_slug=None, album_slug=None, template_name=None, extra_context=None, **kw):
    qs = Photo.objects.published()
    if album_slug:
        qs.filter(album__slug__exact = album_slug)
    return object_detail(request, object_id=id, slug=photo_slug,
            queryset=qs,
            template_name=template_name or 'photogallery/show.html',
            extra_context = extra_context,
            template_object_name='photo')

show = detail # BC

@login_required
@never_cache
def create(request, album_slug=None, form_class=forms.PhotoEdit,  template_name=None, extra_context=None, post_save_redirect=None):
    ctx = {}
    form_init = {}
    album = None
    if album_slug:
        album = Album.objects.published().get(slug=album_slug)
        ctx['album'] = album
        form_init['album'] = album.id
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, initial=form_init)
        if form.is_valid():
            photo = form.save()
            if post_save_redirect:
                return HttpResponseRedirect(post_save_redirect % photo.__dict__)
            elif hasattr(photo, 'get_absolute_url'):
                return HttpResponseRedirect(photo.get_absolute_url())
            else:
                return redirect(reverse='photogallery-photos-show', id=photo.id)
    else:
        form = form_class(initial=form_init)

    ctx['form'] = form
    extra_context = extra_context or {}
    extra_context.update(ctx)

    return render_to_response(template_name or "photogallery/create_photo.html",
            extra_context, RequestContext(request))

@login_required
@never_cache
def edit(request, id, form_class=forms.PhotoEdit, redirect_to=None, template_name=None, extra_context=None):
    try:
        photo = Photo.objects.published().get(id=id)
        if not auth.can_edit_photo(request.user, photo):
            raise Photo.DoesNotExist
    except Photo.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            photo = form.save(commit=False)
            if request.POST.get('create_album'):
                album = Album()
                album.title = request.POST.get('new_album_name')
                request.user.message_set.create(message=_('Album %(name)s created') % {'name': album.title })
                album.save()
                photo.album = album
            if photo.album:
                photo.album.updated_at = datetime.datetime.now()
                photo.album.save(force_update=True)
            photo.save()
            request.user.message_set.create(message=_('Photo updated') if id else _('Photo added'))
            return redirect(redirect_to or photo)
    else:
        form = form_class(instance=photo)

    ctx = extra_context or {}
    ctx.update({
        'form': form, 
        'photo': photo, 
        'can_edit': auth.can_edit_photo(request.user, photo),
        })

    return render_to_response(template_name or 'photogallery/edit_photo.html',
            ctx, RequestContext(request))


@login_required
@never_cache
def delete(request, id, confirm=False, redirect_to=None, template_name=None, extra_context=None):
    try:
        photo = Photo.objects.published().get(id=id)
    except Photo.DoesNotExist:
        raise Http404

    if confirm or request.POST.get('confirm'): 
        photo.delete()
        request.user.message_set.create(message=_('Photo deleted'))
        return redirect(redirect_to or photo.album)

    ctx = extra_context or {}
    ctx.update({
        'photo': photo,
        })
    return render_to_response(template_name or 'photogallery/delete_photo.html',
            ctx, RequestContext(request))

RE_SEARCH_SEPARATOR = re.compile('[\s\+]+')

def search(request, keyword=None, **kwargs):
    request_keyword = keyword or request.REQUEST.get('keyword').strip()
    keywords = RE_SEARCH_SEPARATOR.split(request_keyword)
    queryset = kwargs.get('queryset', Photo.objects)
    extra_context = kwargs.get('extra_context', {})
    if request_keyword:
        tagged = tuple(Photo.tag_objects.with_any(keywords, queryset).values_list('id', flat=True))
        photos = queryset
        for keyword in keywords:
            photos = photos.filter(Q(title__icontains=keyword) |
            Q(description__icontains=keyword) | Q(pk__in=tagged) | Q(album__title__icontains=keyword) |
            Q(album__description__icontains=keyword))
        kwargs['queryset'] = photos
        extra_context['keyword'] = request_keyword
    else:
        kwargs['queryset'] = queryset.none()
    extra_context['search'] = True
    extra_context['found_items_count'] = kwargs['queryset'].count()
    kwargs['extra_context'] = extra_context
    return list(request, **kwargs)
