# Generated by Django 3.0.2 on 2020-02-04 08:45

from django.db import migrations, models
import django.db.models.deletion
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('usersettings', '0004_auto_20200128_1735'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Dateiname')),
                ('cssfile', filebrowser.fields.FileBrowseField(blank=True, max_length=255, verbose_name='css file')),
            ],
            options={
                'verbose_name': 'Theme',
                'verbose_name_plural': 'Themes',
            },
        ),
        migrations.AddField(
            model_name='usersettings',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usersettings.Theme', verbose_name='Theme'),
        ),
    ]
