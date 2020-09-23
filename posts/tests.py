import random
import string

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from .models import Post, Follow


User = get_user_model()


def text_gen(k):
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
    return text


class PlansPageTest(TestCase):
    def setUp(self):
        self.username = text_gen(8)
        self.user = User.objects.create(username=self.username, password='12345678')
        self.client.force_login(self.user)
        cache.clear()

    def test_page_codes(self):
        self.client.logout()
        response = self.client.get('')
        self.assertEqual(response.status_code, 200, msg='Доступ на главную незалогиненым')

    def test_404(self):
        response = self.client.get(f'/{text_gen(10)}', follow=True)
        self.assertEqual(response.status_code, 404, msg='Возврат 404')

    def test_profile(self):
        response = self.client.get(f'/posts/{self.username}/',)
        self.assertEqual(response.status_code, 200, msg='Доступ в профиль')

    def test_new_post_available(self):
        response = self.client.get('/new/',)
        self.assertEqual(response.status_code, 200, msg='Доступ к форме нового поста')
        self.client.logout()
        response = self.client.get('/new/',)
        self.assertRedirects(response, '/auth/login/?next=/new/', status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_post(self):
        text = text_gen(80)
        with open('test_files/test.jpg', 'rb') as img:
            self.client.post('/new/', {'text':text, 'image':img}, follow=True)
        self.assertTrue(Post.objects.filter(text=text).exists())
        post = Post.objects.get(text=text)
        cache.clear()

        response = self.client.get('')
        self.assertContains(response, text,)

        response = self.client.get(f'/posts/{self.username}/')
        self.assertContains(response, text,)

        response = self.client.get(f'/posts/{self.username}/{post.id}/')
        self.assertContains(response, text,)
        self.assertContains(response, '<img')

    def test_wrong_image(self):
        with open('test_files/test.txt', 'rb') as txt:
            response = self.client.post('/new/', {'text':text_gen(80), 'image':txt}, follow=True)
            error_text = response.context['form'].errors['image'].data[0].message
            self.assertFormError(response, 'form', 'image', error_text)

    def test_post_edit(self):
        new_text = text_gen(80)
        post = Post.objects.create(author=self.user, text=text_gen(81))
        self.client.post(f'/posts/{self.username}/{post.id}/edit/', {'text': new_text}, follow=True)
        cache.clear()

        response = self.client.get('')
        self.assertContains(response, new_text)

        response = self.client.get(f'/posts/{self.username}/')
        self.assertContains(response, new_text)

        response = self.client.get(f'/posts/{self.username}/{post.id}/')
        self.assertContains(response, new_text)

    def test_cache(self):
        text = text_gen(80)
        self.client.post('/new/', {'text':text,}, follow=True)
        self.client.get('')
        key = make_template_fragment_key('index_page', ['<QueryDict: {}>'])
        cached_page = cache.get(key)
        self.assertIn(text, cached_page)

    def test_follow(self):
        text = text_gen(80)
        username_2 = text_gen(8)
        user_2 = User.objects.create(username=username_2, password='12345678')
        post = Post.objects.create(author=user_2, text=text)

        self.client.get(f'/posts/{username_2}/follow/', )
        self.assertTrue(Follow.objects.filter(user=self.user, author=user_2).exists())
        response = self.client.get('/follow/')
        self.assertContains(response, text,)

        self.client.get(f'/posts/{username_2}/unfollow/', )
        self.assertFalse(Follow.objects.filter(user=self.user, author=user_2))
        response = self.client.get('/follow/')
        self.assertNotContains(response, text,)

    def test_comment(self):
        text_comment = text_gen(20)
        post = Post.objects.create(author=self.user, text=text_gen(81))

        self.client.post(f'/posts/{self.username}/{post.id}/comment/', {'text': text_comment}, follow=True)
        response = self.client.get(f'/posts/{self.username}/{post.id}/')
        self.assertContains(response, text_comment,)

        self.client.logout()
        response = self.client.get(f'/posts/{self.username}/{post.id}/comment/',)
        self.assertRedirects(response, f'/auth/login/?next=/posts/{self.username}/{post.id}/comment/',
            status_code=302, target_status_code=200, fetch_redirect_response=True)
