from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_user, name="post"),
    path('<id>', views.handle_users, name='handle_users'),
]