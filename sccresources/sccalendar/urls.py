from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<str:service>/<str:event_id>', views.details, name='details'),
    path('search/', views.search, name='search'),
    path('calendars/', views.calendars, name='calendars')
]
