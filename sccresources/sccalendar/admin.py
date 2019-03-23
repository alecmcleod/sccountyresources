from django.contrib import admin

from sccalendar.models import FAQ, StaticEvent
# Register your models here.
admin.site.register(StaticEvent)
admin.site.register(FAQ)