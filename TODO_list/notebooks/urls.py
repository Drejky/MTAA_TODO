from django.urls import path

from . import views

urlpatterns = [
    path('', views.handle_notebooks, name='handle_notebooks'),
    path('<id>', views.handle_notebook, name='handle_notebook'),
    path('<id>/notes/<note_id>', views.handle_notes, name='handle_notes'),
    path('<id>/notes/', views.handle_note, name='handle_note'),
    path('<id>/icon', views.handle_icons, name='handle_icons'),
    path('user/<id>', views.handle_userNotebooks, name='handle_userNotebooks'),

]