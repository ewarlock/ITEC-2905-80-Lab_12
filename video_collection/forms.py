from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    # to make form from video model for user
    class Meta:
        model = Video
        fields = ['name', 'url', 'notes'] # need to match case and spelling of fields in model


class SearchForm(forms.Form):
    # basic django form, not database
    search_term = forms.CharField()