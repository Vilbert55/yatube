from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'index'),
    path('follow/', views.follow_index, name='follow_index'),
    path('new/', views.new_post, name = 'new_post'),
    path('group/<slug>', views.group_posts, name = 'new_group'),
    path('posts/<username>/', views.profile, name='profile'),
    path('posts/<username>/<int:post_id>/', views.post_view, name='post'),
    path('posts/<username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<username>/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<username>/follow/', views.profile_follow, name='profile_follow'),
    path('posts/<username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
]
