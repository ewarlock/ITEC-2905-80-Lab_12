from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # can set messages for user
from django.db.models.functions import Lower # to help with case insensitive sorting
from .forms import SearchForm, VideoForm
from .models import Video

# Create your views here.

def home(request):
    app_name = 'Pet Grooming Videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})


def add(request):
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST) # video form that was filled with info from post request
        if new_video_form.is_valid():
            try:
                # trying this, catching the exceptions we put in the overridden save method in the model
                new_video_form.save()
                return redirect('video_list')
                # messages.info(request, 'New video saved!')
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError: # for duplicate video - error given by DB constraints
                messages.warning(request, 'You already added that video.')
            # TODO: show success method/redirect to list of videos
        messages.warning(request, 'Invalid entry: Please double check information entered in the form.')
        # redisplay page, but still has data the user typed in before
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm() # new video form ready for user to enter data
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})


def video_list(request):
    search_form = SearchForm(request.GET) # build form out of data user has sent to program

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term'] # example: 'husky' or 'persian'
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
    else: # not filled in or first time user sees page
        search_form = SearchForm
        videos = Video.objects.all().order_by(Lower('name'))

    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})


def video_detail(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    return render(request, 'video_collection/video_detail.html', {'video': video})
