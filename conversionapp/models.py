from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class Correspondence(models.Model):
    feed_id = models.IntegerField(blank=True, null=True)
    stop_id = models.CharField(max_length=255, blank=True, null=True,
                                   help_text="Unique identifier for a stop or station.")
    stop_code = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="Uniquer identifier (short text or number) for passengers.")
    stop_name = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Name of stop in local vernacular.")
    stop_desc = models.CharField(
        "description",
        max_length=255, blank=True, null=True,
        help_text='Description of a stop.')
    stop_zone = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Fare zone for a stop ID.")
    stop_url = models.CharField(max_length=255,
                                    blank=True, null=True, help_text="URL for the stop")
    stop_location_type = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Is this a stop or station?")
    stop_parent_station = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="The station associated with the stop")
    stop_timezone = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Timezone of the stop")

    agency_name = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Full name of the transit agency")
    agency_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Unique identifier for transit agency")
    agency_url = models.CharField(max_length=255,
                                      blank=True, null=True, help_text="URL of the transit agency")
    agency_timezone = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Timezone of the agency")
    agency_lang = models.CharField(
        max_length=2, blank=True, null=True,
        help_text="ISO 639-1 code for the primary language")
    agency_phone = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Voice telephone number")
    agency_fare_url = models.CharField(max_length=255,
                                           blank=True, null=True, help_text="URL for purchasing tickets online")

    def __str__(self):
        return '{} '.format(self.id)


class Conversion(models.Model):
    present_str = JSONField(blank=True)
    relace_str = JSONField(blank=True)

    def __str__(self):
        return '{}'.format(self.id)
