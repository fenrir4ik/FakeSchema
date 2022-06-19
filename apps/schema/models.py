from django.contrib.auth.models import User
from django.db import models
from django.db.models import RESTRICT, CASCADE
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Character(models.Model):
    description = models.CharField(max_length=100, unique=True)
    char = models.CharField(max_length=1, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.description} ({self.char})'


class ColumnSeparator(Character, models.Model):
    pass


class StringCharacter(Character, models.Model):
    pass


class DataType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ranged = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Schema(models.Model):
    name = models.CharField(max_length=100)
    modified = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=CASCADE)
    column_separator = models.ForeignKey(ColumnSeparator, on_delete=RESTRICT)
    string_character = models.ForeignKey(StringCharacter, on_delete=RESTRICT)
    data_types = models.ManyToManyField(DataType, related_name='schemas', through='Column')


class Column(models.Model):
    schema = models.ForeignKey(Schema, on_delete=CASCADE)
    type = models.ForeignKey(DataType, on_delete=RESTRICT)
    name = models.CharField(verbose_name="Column name", max_length=100)
    range_start = models.IntegerField(verbose_name="From", null=True, blank=True)
    range_end = models.IntegerField(verbose_name="To", null=True, blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('schema', 'name')


class DataSet(models.Model):
    PREPARING = 'P'
    READY = 'R'
    FAILED = 'F'

    DATASET_STATUS = [
        (PREPARING, 'Preparing'),
        (READY, 'Ready'),
        (FAILED, 'Failed'),
    ]
    created = models.DateField(auto_now=True)
    file = models.FileField(null=True, blank=True)
    schema = models.ForeignKey(Schema, on_delete=CASCADE)
    status = models.CharField(max_length=1, choices=DATASET_STATUS, default=PREPARING)


@receiver(pre_delete, sender=Schema)
def delete_image_from_storage(sender, instance, *args, **kwargs):
    generated_datasets = DataSet.objects.filter(schema_id=instance.id)
    for dataset in generated_datasets:
        dataset.file.delete(True)
