import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Follow
from yatube.settings import NUMBER_POSTS_PER_PAGE

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.group = Group.objects.create(
            title='title_test_group',
            slug='group-test-slug',
            description='group test description',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='X' * 40,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Testing that correct html templates are used in view functions."""
        templates_pages_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse('posts:group', kwargs={'slug': 'group-test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user}'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Testing context dictionary matches the page index."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task = {
            first_object.author.username: 'UserName',
            first_object.text: 'X' * 40,
            first_object.group.slug: 'group-test-slug',
            first_object.image: 'posts/small.gif',
        }
        for task, expected_result in task.items():
            with self.subTest(task=task):
                self.assertEqual(task, expected_result)

    def test_profile_page_show_correct_context(self):
        """Testing context dictionary matches the page profile_page."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': f'{self.user}'})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['posts_count']
        third_object = response.context['username']
        task = {
            first_object.text: 'X' * 40,
            first_object.group.slug: 'group-test-slug',
            second_object: 1,
            third_object.username: 'UserName',
            first_object.image: 'posts/small.gif',
        }
        for task, expected_result in task.items():
            with self.subTest(task=task):
                self.assertEqual(task, expected_result)

    def test_group_list_page_show_correct_context(self):
        """Testing context dictionary matches the page group_list."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'group-test-slug'})
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['group']
        task = {
            first_object.author.username: 'UserName',
            first_object.text: 'X' * 40,
            first_object.group.slug: 'group-test-slug',
            second_object.title: 'title_test_group',
            second_object.description: 'group test description',
            first_object.image: 'posts/small.gif',
        }
        for task, expected_result in task.items():
            with self.subTest(task=task):
                self.assertEqual(task, expected_result)

    def test_post_detail_page_show_correct_context(self):
        """Testing context dictionary matches the page post_detail."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        second_object = response.context['title']
        third_object = response.context['posts_count']
        task = {
            first_object.author.username: 'UserName',
            first_object.text: 'X' * 40,
            first_object.group.slug: 'group-test-slug',
            second_object: 'X' * 29,
            third_object: 1,
            first_object.image: 'posts/small.gif',
        }
        for task, expected_result in task.items():
            with self.subTest(task=task):
                self.assertEqual(task, expected_result)

    def test_post_create_page_show_correct_context(self):
        """Testing context dictionary matches the page post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected_result in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected_result)

    def test_post_edit_page_show_correct_context(self):
        """Testing context dictionary matches the page edit_page."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected_result in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected_result)
        self.assertTrue(response.context['is_edit'])

    def test_comment_available_authorized_client(self):
        """Testing adding a comment is available only to authorized users"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertContains(
            response, '<h5 class="card-header">Добавить комментарий:</h5>'
        )
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertNotContains(
            response, '<h5 class="card-header">Добавить комментарий:</h5>'
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName2')
        cls.group = Group.objects.create(
            title='title_test_group',
            slug='group-test-slug',
            description='group test description',
        )
        cls.posts = list()
        for i in range(1, 13):
            cls.posts.append(
                Post.objects.create
                (
                    author=cls.user,
                    text='X' * i,
                    group=cls.group
                )
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Testing that paginator displays 10 posts on first page."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'group-test-slug'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), NUMBER_POSTS_PER_PAGE
                )

    def test_second_page_contains_two_records(self):
        """Testing that paginator displays 2 posts on second page."""
        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'group-test-slug'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    12 - NUMBER_POSTS_PER_PAGE
                )


class CorrectDisplayPostsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.group = Group.objects.create(
            title='title_test_group',
            slug='group-test-slug',
            description='group test description',
        )
        cls.group2 = Group.objects.create(
            title='title_test_group2',
            slug='group-test-slug2',
            description='group test description2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post display on three pages',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_group_profile_display_new_post(self):
        """Testing that new post displays on pages: index, group, profile."""
        cache.clear()
        pages = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'group-test-slug'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertContains(
                    response, 'Test post display on three pages'
                )

    def test_not_display_new_post_in_another_group(self):
        """Testing that a post not displays on pages of other groups."""
        response = self.client.get(
            reverse('posts:group', kwargs={'slug': 'group-test-slug2'})
        )
        self.assertNotContains(
            response, 'Test post display on three pages'
        )


class TestCashIndexPage(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post display 20 sek on the index page',
        )

    def setUp(self):
        cache.clear()

    def test_display_post_after_deletion(self):
        """Testing that a post displays on the index page after deletion
         and doesn't display after clear cash."""
        response = self.client.get(reverse('posts:index'))
        self.post.delete()
        self.assertContains(
            response, 'Test post display 20 sek on the index page'
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotContains(
            response, 'Test post display 20 sek on the index page'
        )


class FollowUnfollowTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.user2 = User.objects.create_user(username='UserName2')
        cls.post = Post.objects.create(
            author=cls.user,
            text='X' * 40,
        )
        cls.subscription = Follow.objects.create(
            author=cls.user,
            user=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow(self):
        """Test to create a new follow record in the database."""
        subscription_count = Follow.objects.count()
        new_subscription = {
            'author': self.user2,
            'user': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.user2}),
            data=new_subscription,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user2}
            )
        )
        self.assertEqual(Follow.objects.count(), subscription_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                author=self.user2,
                user=self.user,
            ).exists()
        )

    def test_unfollow(self):
        """Test to delete an unfollow record in the database."""
        subscription_count = Follow.objects.count()
        subscrition = Follow.objects.filter(author=self.user)
        subscrition.delete()
        self.assertEqual(Follow.objects.count(), subscription_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                author=self.user2,
                user=self.user,
            ).exists()
        )

    def test_display_post_on_subscription_page(self):
        """Testing that post displays on subscription page."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(
            response, 'X' * 40
        )

    def test_not_display_post_on_subscription_page(self):
        """Testing that post doesn't display if you aren't subscribed
         to the author."""
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(
            response, 'X' * 40
        )
