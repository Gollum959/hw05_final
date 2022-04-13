from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoBody')
        cls.group = Group.objects.create(
            title='test_grope',
            slug='test-slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='X' * 20,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_called_html_templates(self):
        """Check called html templates."""
        task = self.post
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group', kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{task.author}'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': task.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': task.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_access(self):
        """Testing page access."""
        task = self.post
        templates_url_user = {
            reverse('posts:index'): self.guest_client,
            reverse(
                'posts:group', kwargs={'slug': f'{self.group.slug}'}
            ): self.guest_client,
            reverse('posts:profile', kwargs={'username': f'{task.author}'}):
            self.guest_client,
            reverse('posts:post_detail', kwargs={'post_id': task.id}):
            self.guest_client,
            reverse('posts:post_edit', kwargs={'post_id': task.id}):
            self.authorized_client,
            reverse('posts:post_create'): self.authorized_client,
        }
        for address, type_user in templates_url_user.items():
            with self.subTest(address=address):
                response = type_user.get(address)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_create_page_redirect_anonymous_on_login_page(self):
        """Testing a redirect from the post creation page of an unauthorized
         user to the authorization page."""
        response = self.guest_client.get(
            reverse('posts:post_create'), follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_post_page_redirect_not_author_on_post_info_page(self):
        """Testing a redirect from the post edit page of a not-post author
         to the post details page."""
        task = self.post
        not_author_user = User.objects.create_user(username='NoNone')
        not_author_authorized_client = Client()
        not_author_authorized_client.force_login(not_author_user)
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': task.id}),
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{task.id}/edit/'
        )

    def test_unexistin_page_return_404(self):
        """Testing unexist page return 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_create_comment_redirect_anonymous_on_login_page(self):
        """Attempting to access the address where the comment was created will
         redirect an unauthorized user to the authorization page."""
        task = self.post
        response = self.guest_client.get(
            reverse(
                'posts:add_comment', kwargs={'post_id': task.id}
            )
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{task.id}/comment/'
        )
