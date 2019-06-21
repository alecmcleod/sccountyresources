from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<str:service>/<str:event_id>/', views.details, name='details'),
    path('search/', views.search, name='search'),
    path('search/day/', views.search_day_noncomplete, name='search_day_noncomplete'),
    path('search/day/<int:year>/<int:month>/<int:day>/', views.search_day, name='search_day'),
    path('download/event/<str:service>/<str:event_id>/', views.event_ical_download, name='download_event'),
    path('download/calendar/<str:service>/', views.calendar_ical_download, name='download_calendar'),
    path('calendars/', views.calendars, name='calendars'),
    path('confirm/', views.subscribe, name='confirm'),
    path('confirm/result/', views.confirm, name='result'),
    path('cancel/', views.unsubscribe, name='ubsubscribe'),
    path('faq/', views.faq, name='FAQ'),
    path('events/', views.events, name="events"),
    path('contactus/', views.contact_us, name="contact_us"),
    path('djrichtextfield/', include('djrichtextfield.urls')),
]
