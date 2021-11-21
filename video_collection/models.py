from django.db import models
from urllib import parse 
from django.core.exceptions import ValidationError

# Create your models here.

class Video(models.Model):
    name = models.CharField(max_length=200) # must specify character length for CharField
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True) # makes it not required
    video_id = models.CharField(max_length=40, unique=True)

    # override save method for this class, code runs before django saves data
    def save(self, *args, **kwargs):
        # arguments, keyword arguments
        # extract video ID from youtube url
        # raise exception if URL is not valid
        #if not self.url.startswith('https://www.youtube.com/watch'):
        #    raise ValidationError(f'Not a YouTube URL {self.url}')

        url_components = parse.urlparse(self.url)

        if url_components.scheme != 'https':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.path != '/watch':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        query_string = url_components.query # example 'v=dks3e4r3'
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) # dictionary
        v_parameters_list = parameters.get('v') # return None if no key found
        if not v_parameters_list: # None or empty list
            raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')
        self.video_id = v_parameters_list[0]

        # call django's save function so django's save still runs
        super().save(*args, **kwargs)

        # in admin, the video id field will be overwritten if I enter something in there
    
    def __str__(self):
        # string with id, name, url, and only first 200 chars of notes
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video ID: {self.video_id}, Notes: {self.notes[:200]}'


