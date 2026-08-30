from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('feeds', views.feeds_check, name='feed_list'),
    path('feeds/toggle', views.toggle_feed, name='toggle_feed'),
    path('refresh-feeds', views.refresh_function_view, name='refresh_feeds'),
]
