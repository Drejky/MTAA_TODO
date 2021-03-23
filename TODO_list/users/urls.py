from django.urls import path

from . import views

urlpatterns = [
    path('', views.handle_users, name="post"),
    path('<id>', views.handle_users, name='handle_users'),
]