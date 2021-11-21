from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.utils import teardown_databases
from django.urls import reverse

from .models import Video
# to run: python manage.py test


class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        # can look up URL by name
        url = reverse('home') # generates correct URL
        response = self.client.get(url) # django test case has client we can make requests to
        self.assertContains(response, 'Pet Grooming Videos') # can test something is in the response


class TestAddVideos(TestCase):
    
    def test_add_video(self):
        valid_video = {
            'name': 'Dog changes color',
            'url': 'https://www.youtube.com/watch?v=Kn_lCyiGEbQ',
            'notes': 'this dog changes color after a haircut'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True) # post request expects data in key value pairs. follow=True - follow the redirect

        self.assertTemplateUsed('video_collection/video_list.html')

        # video list show new video?
        self.assertContains(response, 'Dog changes color')
        self.assertContains(response, 'this dog changes color after a haircut')
        self.assertContains(response, 'https://www.youtube.com/watch?v=Kn_lCyiGEbQ')

        # 1 video in db?
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # can query db to see if the specific video was added
        video = Video.objects.first() # this is our example video since this is the only video in the db
        self.assertEqual(valid_video['name'], video.name)
        self.assertEqual(valid_video['url'], video.url)
        self.assertEqual(valid_video['notes'], video.notes)
        self.assertEqual('Kn_lCyiGEbQ', video.video_id)


    def test_add_video_invalid_url_not_added(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abcdef=Kn_lCyiGEbQ',
            'https://www.youtube.com/watch?v=',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=Kn_lCyiGEbQ',
        ]

        for invalid_video_url in invalid_video_urls:
            new_video = {
            'name': 'Name',
            'url': invalid_video_url,
            'notes': 'Example notes'
            }
            url = reverse('add_video')
            response = self.client.post(url, new_video)

            self.assertTemplateUsed('video_collection/add.html')
            messages = response.context['messages']
            message_text = [ message.message for message in messages] # extract message's message for every message in message list

            self.assertIn('Invalid YouTube URL', message_text) # string inside list?
            self.assertIn('Invalid entry: Please double check information entered in the form.', message_text)
            # make sure videos not in db
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    
    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='ZZZ', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')
        expected_video_order = [v2, v1, v4, v3]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos']) # context is the data that is given to the template

        self.assertEqual(videos_in_template, expected_video_order)


    def test_no_videos_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos found.')
        self.assertEqual(0, len(response.context['videos']))   


    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')    

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video:')
        self.assertNotContains(response, '1 videos:')
        self.assertEqual(1, len(response.context['videos']))  


    def test_video_number_message_four_videos(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='ZZZ', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')

        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '4 videos:')
        self.assertNotContains(response, '4 video:')
        self.assertEqual(4, len(response.context['videos'])) 


class TestVideoSearch(TestCase):


    def test_video_search_matches(self):
        v1 = Video.objects.create(name='Another zany video name', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='another short video name', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='youtube!!!!!', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')
        v4 = Video.objects.create(name='This one is different', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        expected_video_order = [v2, v1]

        response = self.client.get(reverse('video_list') + '?search_term=another')
        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)       


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='Another long video name', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='another short video name', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='youtube!!!!!', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')
        v4 = Video.objects.create(name='This one is different', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        expected_video_order = []

        response = self.client.get(reverse('video_list') + '?search_term=zzzzzzzzzzzzzzzzz')
        videos_in_template = list(response.context['videos'])

        self.assertEqual(videos_in_template, expected_video_order)        
        self.assertContains(response, 'No videos found.')


class TestVideoDetail(TestCase):


    def test_video_detail_displays_video_information_for_video_that_exists(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='ZZZ', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')

        video = Video.objects.get(pk=1)
        response = self.client.get(reverse('video_detail', kwargs={'video_pk': 1} ))

        self.assertTemplateUsed(response, 'video_collection/video_detail.html')
        video_detail_data = response.context['video']
        self.assertEqual(video_detail_data, video)

        expected_video_details = ['ID: 1', 'Name: abc', 'URL: https://www.youtube.com/watch?v=Kn_lCyiGEbQ', 'Video ID: Kn_lCyiGEbQ', 'Notes: example']
        for expected_video_detail in expected_video_details:
            self.assertContains(response, expected_video_detail)


    def test_video_detail_displays_video_information_for_video_that_exists_with_no_notes(self):
        v1 = Video.objects.create(name='abc', notes='', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='ZZZ', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')

        video = Video.objects.get(pk=1)
        response = self.client.get(reverse('video_detail', kwargs={'video_pk': 1} ))

        self.assertTemplateUsed(response, 'video_collection/video_detail.html')
        video_detail_data = response.context['video']
        self.assertEqual(video_detail_data, video)

        expected_video_details = ['ID: 1', 'Name: abc', 'URL: https://www.youtube.com/watch?v=Kn_lCyiGEbQ', 'Video ID: Kn_lCyiGEbQ', 'No notes for this video.']
        for expected_video_detail in expected_video_details:
            self.assertContains(response, expected_video_detail)


    def test_video_detail_displays_404_if_video_not_in_db(self):
        v1 = Video.objects.create(name='abc', notes='', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=xy4e-R8FiR4')
        v3 = Video.objects.create(name='ZZZ', notes='example', url='https://www.youtube.com/watch?v=NvUYUYNcaTE')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=od7F_hTlC1g')

        response = self.client.get(reverse('video_detail', kwargs={'video_pk': 12} ))

        self.assertEqual(404, response.status_code)



class TestVideoModel(TestCase):
    
    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='Another long video name', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='Another long video name', notes='example', url='https://www.youtube.com/watch?v=Kn_lCyiGEbQ')

    
    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch/somethingelse',
            'http://www.youtube.com/watch/somethingelse?v=Kn_lCyiGEbQ',
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abcdef=Kn_lCyiGEbQ',
            'https://www.youtube.com/watch?v=',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=Kn_lCyiGEbQ',
            'http://www.youtube.com/watch?v=Kn_lCyiGEbQ',
            '',
            'hhhhhttps://www.youtube.com/watch/somethingelse?v=Kn_lCyiGEbQ',
            '👻👻👻👻👻👻👻👻👻👻'
        ]
        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='Another long video name', notes='example', url=invalid_video_url)

        self.assertEqual(0, Video.objects.count())