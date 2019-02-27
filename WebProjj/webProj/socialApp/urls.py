
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.hobbies, name='signup'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('homepage/', views.homepage, name='homepage'),
    path('findMatches/', views.matches, name='findMatches'),
    path('findMatches/getMatches/', views.getMatches, name='getMatches'),
    path('findMatches/poke/', views.poke, name="poke")

]

# TODO
