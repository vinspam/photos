# Generated by Django 3.0.4 on 2020-03-24 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersettings', '0012_auto_20200310_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Name'),
        ),
    ]