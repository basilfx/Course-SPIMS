from django.db import models

class Record(models.Model):
    model = models.CharField(max_length=64)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    session_id = models.BigIntegerField()

    sensor_da2_max = models.FloatField()

    max_ax = models.FloatField()
    max_ay = models.FloatField()
    max_az = models.FloatField()
    min_ax = models.FloatField()
    min_ay = models.FloatField()
    min_az = models.FloatField()

    rounds = models.IntegerField()
    acc_change = models.IntegerField()