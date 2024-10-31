# Generated by Django 4.0.6 on 2022-07-13 08:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0023_rename_event_photo_gallery'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallery',
            options={'ordering': ['-timestamp'], 'verbose_name': 'gallery', 'verbose_name_plural': 'galleries'},
        ),
        migrations.AlterField(
            model_name='photo',
            name='gallery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='photos.gallery', verbose_name='gallery'),
        ),
    ]
