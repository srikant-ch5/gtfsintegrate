# Generated by Django 2.0.6 on 2018-06-27 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multigtfs', '0001_initial'),
        ('osmapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='feed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multigtfs.Feed'),
        ),
        migrations.AddField(
            model_name='osm_relation',
            name='feed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multigtfs.Feed'),
        ),
        migrations.AddField(
            model_name='way',
            name='feed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multigtfs.Feed'),
        ),
    ]