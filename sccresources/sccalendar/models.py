from django.db import models

class Event(models.Model):
	event_id = models.CharField(max_length=100)
	calendar_id = models.CharField(max_length=100)
	iso_date_time = models.CharField(max_length=30)

class Number(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	number = models.CharField(max_length=13)
