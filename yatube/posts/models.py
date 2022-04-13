from django.db import models
from django.contrib.auth import get_user_model

from core.models import AutoDateModel

User = get_user_model()


class Post(AutoDateModel):
    text = models.TextField('Текст поста', help_text="Введите текст поста")
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='groups',
        verbose_name='Group',
        help_text="Группа, к которой будет относиться пост",
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.text[:15]}'

    class Meta:
        ordering = ('-pub_date',)


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return f'{self.title}'


class Comment(AutoDateModel):
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.text}'


class Follow (models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
