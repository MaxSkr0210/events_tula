from django.db import models

class Events(models.Model):
    event_name = models.TextField()
    description = models.TextField()
    age_restrictions = models.TextField()
    company = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    address = models.TextField()
    img_link = models.TextField()
    is_registered = models.BooleanField()

    class Meta:
        managed = False
        verbose_name = "Мероприятия"
        verbose_name_plural = "Мероприятия"
        ordering: ["is_registered"]
        db_table = 'event'

class Reminders(models.Model):
    event_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    reminder_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Напоминания"
        verbose_name_plural = "Напоминания"
        managed = False
        db_table = 'reminders'


class Users(models.Model):
    chat_id = models.IntegerField(blank=True, null=True)
    event = models.ForeignKey(Events, models.DO_NOTHING, blank=True, null=True)
    is_registered = models.BooleanField(blank=True, null=True)

    class Meta:
        verbose_name = "Посетители"
        verbose_name_plural = "Посетители"
        managed = False
        db_table = 'users'