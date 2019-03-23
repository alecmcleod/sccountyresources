from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Event(models.Model):
    event_id = models.CharField(max_length=100)
    calendar_id = models.CharField(max_length=100)
    iso_date_time = models.CharField(max_length=30)


class Number(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    number = models.CharField(max_length=13)

class FAQ(models.Model):
    question = models.CharField(max_length=200, help_text='The Frequently Asked Question')
    answer = models.TextField(help_text='Answer to the question')

    def __str__(self):
        return self.question

class StaticEvent(models.Model):
    """ Defines non-changing events that can be displayed as a list"""

    # Fields
    event_name = models.CharField(max_length=100, help_text='Enter event name')
    event_details = models.CharField(max_length=200, help_text='Enter event details (times ect.)', blank=True, null=True)
    event_address = models.CharField(max_length=200, blank=True, null=True, help_text='Enter event address')
    event_phone = PhoneNumberField(blank=True, null=True)
    event_email = models.EmailField(blank=True, null=True)
    event_url = models.URLField(max_length=200, blank=True, null=True)

    # Metadata
    class meta:
        ordering = ['event_name']

    # Methods
    def __str__(self):
        return self.event_name

