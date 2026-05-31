from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


import authentication.views
import blog.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', authentication.views.login_page, name='login'),

    path('signup/', authentication.views.signup_page, name='signup'),

    path('tickets/create/', blog.views.ticket_create, name='ticket_create'),
    path('tickets/<int:ticket_id>/edit/', blog.views.ticket_update, name='ticket_update'),
    path('tickets/<int:ticket_id>/delete/', blog.views.ticket_delete, name='ticket_delete'),

    path('reviews/create/', blog.views.review_create, name='review_create'),
    path('reviews/<int:review_id>/edit/', blog.views.review_update, name='review_update'),
    path('reviews/<int:review_id>/delete/', blog.views.review_delete, name='review_delete'),
    path('tickets/<int:ticket_id>/review/', blog.views.review_reply, name='review_reply'),

    path('posts/', blog.views.posts_list, name='posts_list'),
    path('feed/', blog.views.feed, name='feed'),

    path('subscriptions/', blog.views.subscriptions, name='subscriptions'),
    path('subscriptions/follow/', blog.views.follow_user, name='follow_user'),
    path('subscriptions/unfollow/<int:user_id>/', blog.views.unsubscribe, name='unsubscribe'),

    path('logout/', authentication.views.logout_user, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
