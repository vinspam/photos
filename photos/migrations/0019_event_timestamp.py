# Generated by Django 3.0.6 on 2020-05-14 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0018_event_visible_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='timestamp',
            field=models.DateTimeField(auto_created=True, null=True, verbose_name='timestamp'),
        ),
    ]
