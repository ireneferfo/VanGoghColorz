from django.views import generic
from vg_app.models import Picture, Artist
from random import randint
from django.db.models import Max, Q
from django.shortcuts import render, redirect
from .color_filter import color_is_near
from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json
import csv


def index(request):
    return render(request, 'index.html')


def random_picture_detail(request):
    picture = Picture.objects.all()
    max = picture.aggregate(Max('id'))
    pk = randint(1, max['id__max'])
    return redirect('vg_app:picture-detail', pk=pk)


def download_picture_csv(request):
    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; filename="pictures.csv"'})
    model = Picture
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    writer = csv.writer(response)
    writer.writerow(field_names)
    title = request.GET.get('title')
    year = request.GET.get('year')
    artist = request.GET.get('artist')
    gallery = request.GET.get('gallery')
    tags = request.GET.get('tags')
    color = request.GET.get('color')
    q = Q()
    if title:
        q &= Q(Title__icontains=title)
    if year:
        q &= Q(Year__icontains=year)
    if artist:
        q &= Q(Artist__Name__icontains=artist)
    if gallery:
        q &= Q(Gallery_name__icontains=gallery)
    if tags:
        q &= Q(Tags__icontains=tags)
    object_list = Picture.objects.filter(q)
    if color:
        ids = [picture.id for picture in object_list if color_is_near(picture, color)]
        object_list = object_list.filter(id__in=ids)

    for row in object_list:
        values = []
        for field in field_names:
            if field == "Artist":
                value = row.Artist.Name
            elif field == "Color":
                value = '{'
                for color in row.Color.all():
                    value += color.Color + ': ' + str(color.Quantity) + ', '
                value = value[:-2] + '}'
            else:
                value = getattr(row, field)
            if value is None:
                value = ''
            values.append(value)
        writer.writerow(values)

    return response


def download_picture_json(request):
    model = Picture
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    title = request.GET.get('title')
    year = request.GET.get('year')
    artist = request.GET.get('artist')
    gallery = request.GET.get('gallery')
    tags = request.GET.get('tags')
    color = request.GET.get('color')
    q = Q()
    if title:
        q &= Q(Title__icontains=title)
    if year:
        q &= Q(Year__icontains=year)
    if artist:
        q &= Q(Artist__Name__icontains=artist)
    if gallery:
        q &= Q(Gallery_name__icontains=gallery)
    if tags:
        q &= Q(Tags__icontains=tags)
    object_list = Picture.objects.filter(q)
    if color:
        ids = [picture.id for picture in object_list if color_is_near(picture, color)]
        object_list = object_list.filter(id__in=ids)

    data = []
    for row in object_list:
        values = {}
        for field in field_names:
            if field == "Artist":
                value = row.Artist.Name
            elif field == "Color":
                value = {}
                for n, color in enumerate(row.Color.all()):
                    color_dict = {'color': color.Color, 'quantity': color.Quantity}
                    value[str(n)] = color_dict
            else:
                value = getattr(row, field)
            if value is None:
                value = ''
            values[field] = value
        data.append(values)

    picture_json = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(picture_json, content_type='application/json')


def download_picture_xml(request):
    title = request.GET.get('title')
    year = request.GET.get('year')
    artist = request.GET.get('artist')
    gallery = request.GET.get('gallery')
    tags = request.GET.get('tags')
    color = request.GET.get('color')
    q = Q()
    if title:
        q &= Q(Title__icontains=title)
    if year:
        q &= Q(Year__icontains=year)
    if artist:
        q &= Q(Artist__Name__icontains=artist)
    if gallery:
        q &= Q(Gallery_name__icontains=gallery)
    if tags:
        q &= Q(Tags__icontains=tags)
    object_list = Picture.objects.filter(q)
    if color:
        ids = [picture.id for picture in object_list if color_is_near(picture, color)]
        object_list = object_list.filter(id__in=ids)

    with open('picture.xml', 'w') as f:
        serializers.serialize("xml", object_list, stream=f)
    with open('picture.xml', 'r') as f:
        response = HttpResponse(f, content_type='text/xml', headers={'Content-Disposition': 'attachment; filename="picture.xml"'})
        return response


def download_artist_csv(request):
    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; filename="artist.csv"'})
    model = Artist
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    writer = csv.writer(response)
    writer.writerow(field_names)
    object_list = Artist.objects.all()

    for row in object_list:
        values = []
        for field in field_names:
            value = getattr(row, field)
            if value is None:
                value = ''
            values.append(value)
        writer.writerow(values)

    return response


def download_artist_json(request):
    model = Artist
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    object_list = Artist.objects.all()

    data = []
    for row in object_list:
        values = {}
        for field in field_names:
            value = getattr(row, field)
            if value is None:
                value = ''
            values[field] = value
        data.append(values)

    artist_json = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(artist_json, content_type='application/json')


def download_artist_xml(request):
    with open('artist.xml', 'w') as f:
        serializers.serialize("xml", Artist.objects.all(), stream=f)
    with open('artist.xml', 'r') as f:
        response = HttpResponse(f, content_type='text/xml', headers={'Content-Disposition': 'attachment; filename="artist.xml"'})
        return response


def download_image(request):
    artist = request.GET.get('artist')
    year = request.GET.get('year')
    id = request.GET.get('id')
    fl_path = 'vg_app/static/images/'+artist+'/'+year+'/'+id+'.jpg'
    q = Q(Picture_ID__icontains=id)
    object_list = Picture.objects.filter(q)
    filename = object_list[0].Title.replace(' ', '_')

    fl = open(fl_path, 'rb')
    response = HttpResponse(fl, content_type='image/jpeg')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


class PictureListView(generic.ListView):
    model = Picture
    paginate_by = 10

    def get_queryset(self):
        title = self.request.GET.get('title')
        year = self.request.GET.get('year')
        artist = self.request.GET.get('artist')
        gallery = self.request.GET.get('gallery')
        paintedin = self.request.GET.get('paintedin')
        tags = self.request.GET.get('tags')
        color = self.request.GET.get('color')
        q = Q()
        if title:
            q &= Q(Title__icontains=title)
        if year:
            q &= Q(Year__icontains=year)
        if artist:
            q &= Q(Artist__Name__icontains=artist)
        if gallery:
            q &= Q(Gallery_name__icontains=gallery)
        if paintedin:
            q &= Q(Location__icontains=paintedin)
        if tags:
            q &= Q(Tags__icontains=tags)
        object_list = Picture.objects.filter(q)
        if color:
            ids = [picture.id for picture in object_list if color_is_near(picture, color)]
            object_list = object_list.filter(id__in=ids)
        return object_list


class PictureDetailView(generic.DetailView):
    model = Picture


class ArtistListView(generic.ListView):
    model = Artist


class ArtistDetailView(generic.DetailView):
    model = Artist
