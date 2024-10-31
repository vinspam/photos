# Generated by Django 3.0.2 on 2020-02-02 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0016_auto_20200130_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='photos.Event', verbose_name='event'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='tags',
            field=models.ManyToManyField(blank=True, to='photos.Tag', verbose_name='tag'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='upload',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='photos.Import', verbose_name='import'),
        ),
    ]
