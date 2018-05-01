from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<str:event_id>', views.details, name='details'),
]