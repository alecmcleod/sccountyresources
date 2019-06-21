from django.db import models
from djrichtextfield.models import RichTextField


class Event(models.Model):
    event_id = models.CharField(max_length=100)
    calendar_id = models.CharField(max_length=100)
    iso_date_time = models.CharField(max_length=30)


class Number(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    number = models.CharField(max_length=13)

class FAQ(models.Model):
    question = models.CharField(max_length=200, help_text='The Frequently Asked Question')
    answer = RichTextField(help_text='Answer to the question')

    def __str__(self):
        return self.question

class StaticEvent(models.Model):
    """ Defines non-changing events that can be displayed as a list"""

    # Fields
    event_name = models.CharField(max_length=100, help_text='Enter event name')
    event_details = models.CharField(max_length=200, help_text='Enter event details (times ect.)', blank=True, null=True)
    event_address = models.CharField(max_length=200, blank=True, null=True, help_text='Enter event address')
    event_phone = models.CharField(max_length=40, blank=True, null=True, help_text='Enter phone number')
    event_email = models.EmailField(blank=True, null=True)
    event_url = models.URLField(max_length=200, blank=True, null=True)

    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)


    # Metadata
    class meta:
        ordering = ['event_name']

    # Methods
    def __str__(self):
        return self.event_name

class Area(models.Model):
    """Model representing an area for a static event e.g. Santa Cruz or Watsonville"""
    name = models.CharField(max_length=200, help_text='Enter the area name')

    def __str__(self):
        """String for representing the Model object"""
        return self.name

class Category(models.Model):
    """Model representing a category for a static event e.g. Shelter, Food"""
    name = models.CharField(max_length=200, help_text='Enter the category title')

    def __str__(self):
        """String for representing the Model object"""
        return self.name