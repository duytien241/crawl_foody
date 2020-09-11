"""webping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from app import views
from django.contrib.auth import views as auth_views
from app.forms import EmailValidationOnForgotPassword
from app.api import urls


urlpatterns = [
    path('healthz', views.healthz, name='healthz'),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'),
         name="logout"),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='pages/password_reset.html',
             form_class=EmailValidationOnForgotPassword,
             email_template_name='pages/password_reset_email.html',
             subject_template_name='pages/password_reset_subject.html'),
         name='password_reset'),
    path('password_reset/done',
         auth_views.PasswordResetDoneView.as_view(
             template_name='pages/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset_confirm//<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='pages/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='pages/password_reset_complete.html'),
         name='password_reset_complete'),
    path('websites/', views.websites, name='websites'),
    path('manageaddress/', views.manageNotificationAddress, name='manageaddress'),
    path('manageaddress/<uuid:id>', views.manageNotificationAddressOfUrl, name='manageaddress'),
    path('changes/<uuid:id>', views.viewChanges, name='changes'),
    path('historycompare/<uuid:id>', views.viewHistoryCompare, name='history-changes'),
    path('', include(urls)),
]