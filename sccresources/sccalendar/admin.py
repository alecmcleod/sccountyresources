from django.contrib import admin

from sccalendar.models import FAQ, StaticEvent, Area, Category
# Register your models here.
admin.site.register(StaticEvent)
admin.site.register(Area)
admin.site.register(Category)

admin.site.register(FAQ)