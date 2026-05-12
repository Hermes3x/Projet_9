from django.contrib import admin
from django.urls import path, include
from blog import views


import authentication.views
import blog.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', authentication.views.login_page, name='login'),
    path('home/', blog.views.home, name='home'),
    path('logout/', authentication.views.logout_user, name='logout'),
    path('signup/', authentication.views.signup_page, name='signup'),
    path('hello/', views.hello, name='hello'),
]
