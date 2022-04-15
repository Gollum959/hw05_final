from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from yatube.settings import NUMBER_POSTS_PER_PAGE


def index(request: HttpRequest) -> HttpResponse:
    """Home page."""
    posts = Post.objects.select_related('group').select_related('author').all()
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': create_paginator(request, posts),
        'index': True
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Page to display posts of one group."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.select_related('author').all()
    context = {
        'group': group,
        'page_obj': create_paginator(request, posts),
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """User information page."""
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('group').all()
    following = None
    if request.user.is_authenticated:
        sub = Follow.objects.filter(author=user, user=request.user)
        following = True if sub else False
    context = {
        'posts_count': posts.count(),
        'page_obj': create_paginator(request, posts),
        'username': user,
        'following': following,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Page to display post details."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    posts_count = post.author.posts.all().count()
    form = CommentForm()
    context = {
        'post': post,
        'title': post.text[:29],
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Page to create a new post for logged in users."""
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    if form.is_valid():
        save_form_to_db(form, request.user)
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Page to edit a post for logged in user."""
    post = get_object_or_404(Post, pk=post_id)
    if request.method != 'POST' and post.author == request.user:
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/create_post.html', context)
    if request.method != 'POST' and post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST,
        instance=post,
        files=request.FILES or None,
    )
    if form.is_valid():
        save_form_to_db(form, request.user)
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Add a comment to a post by an authorized user."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """"Subscription page."""
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('group').select_related('author')
    context = {
        'title': 'Подписки',
        'page_obj': create_paginator(request, posts),
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Add author to subscriptions."""
    user = get_object_or_404(User, username=username)
    if user == request.user:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(
        author=user,
        user=request.user,
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Remove author from subscriptions."""
    user = get_object_or_404(User, username=username)
    sub = Follow.objects.filter(author=user, user=request.user)
    sub.delete()
    return redirect('posts:profile', username=username)


def save_form_to_db(form: PostForm, user: User) -> None:
    """"Save post to DB."""
    post = form.save(commit=False)
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.author = user
    post.save()


def create_paginator(request: HttpRequest, posts: Post) -> Paginator:
    """Create paginator"""
    paginator = Paginator(posts, NUMBER_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
