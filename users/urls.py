from django.urls import path, include
from . import views

# app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    # path('accounts/', include('allauth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('accounts/profile/', views.profile, name='profile'),
]

