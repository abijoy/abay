
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as users_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', users_views.home, name='home'),
    path('register/', users_views.register, name='register'),
    path('login/', users_views.login_view, name='login'),
    path('verify/x/<str:token>/', users_views.verify_account, name='users-verify'),
    path('verify/email/', users_views.verify_email_verification_code, name='verify-email'),
    path('verify/new/code/', users_views.get_email_verification_code, name='get-verification-code'),
    path('myview/', users_views.myview),

]
