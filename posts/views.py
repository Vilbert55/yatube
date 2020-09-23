from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, decorators
from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


def index(request, order='-pub_date'):
    if request.GET.get('order') == '-comments_count':
        order = request.GET.get('order')
    post_list = Post.objects.select_related('author').all().annotate(comments_count=Count('comments')).order_by(order)
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
        {'page': page, 'paginator': paginator, 'request': request, 'order':order})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('author').filter(group_id=group.pk).order_by('-pub_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page':page, 'paginator': paginator, })


@decorators.login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, )
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form':form})
    form = PostForm()
    return render(request, 'new_post.html', {'form':form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author_id=author.pk).order_by('-pub_date').all()
    paginator = Paginator(posts, 5)
    post_count = posts.count
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author).exists()
    return render(request, 'profile.html',
        {'author':author, 'page':page, 'paginator': paginator, 'post_count':post_count, 'following':following })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    comments = Comment.objects.filter(post_id=post_id).order_by('-created').all()
    paginator = Paginator(comments, 4)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    return render(request, 'post.html', {'post':post, 'form':form,  'page':page, 'paginator': paginator, 'username':author})


@decorators.login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post_obj = get_object_or_404(Post, pk=post_id)
    if post_obj.author != request.user != user:
        return redirect('post', username=username, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post_obj)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'new_post.html', {'post':post_obj, 'form':form})

    form = PostForm(instance=post_obj)
    return render(request, 'new_post.html', {'post':post_obj, 'form':form})


@decorators.login_required
def add_comment(request, username, post_id):
    get_object_or_404(User, username=username)
    post_obj = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST or None, )
        if form.is_valid():
            form.instance.author = request.user
            form.instance.post = post_obj
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'post.html', {'form':form, 'post':post_obj})

    form = CommentForm()
    return render(request, 'post.html', {'form':form, 'post':post_obj})


@decorators.login_required
def follow_index(request):
    following_authors = request.user.follower.all().values_list('author')
    post_list = Post.objects.select_related('author').filter(
        author__in=following_authors).order_by('-pub_date')
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@decorators.login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    already_follows = Follow.objects.filter(user=request.user, author=user).exists()
    if user != request.user and not already_follows:
        Follow.objects.create(user=request.user, author=user)
    return redirect('profile', username=username)


@decorators.login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=user).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
