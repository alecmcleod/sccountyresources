from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<str:service>/<str:event_id>', views.details, name='details'),
    path('search/', views.search, name='search'),
    path('download/event/<str:service>/<str:event_id>', views.event_ical_download, name='download_event'),
    path('download/calendar/<str:service>', views.calendar_ical_download, name='download_calendar'),
    path('calendars/', views.calendars, name='calendars'),
    path('confirm/', views.subscribe, name='confirm'),
    path('confirm/result/', views.confirm, name='result'),
    path('cancel/', views.unsubscribe, name='ubsubscribe'),
]
