from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_user, name="post"),
    path('<id>', views.handle_users, name='handle_users'),
    path('auth/login', views.login_request, name='login'),
    path('auth/valid', views.check_if_token_is_valid, name='validation'),
    path('user/', views.handle_userByName, name='handle_userByName'),
]
