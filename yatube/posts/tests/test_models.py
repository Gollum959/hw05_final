from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test_grope',
            slug='test-slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='X' * 20,
        )

    def test_models_have_correct_object_names(self):
        """Testing the __str__ method for classes Post and Group."""
        task = PostModelTest.group
        self.assertEqual(task.__str__(), task.title)
        task = PostModelTest.post
        self.assertEqual(task.__str__(), task.text[:15])

    def test_verbose_name(self):
        """Testing verbose_name and help_text for model Post."""
        task = PostModelTest.post
        field_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Group',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value
                )
