# Generated by Django 2.0.6 on 2018-06-22 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osmapp', '0003_auto_20180622_2042'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FeedBound',
            new_name='FeedBounds',
        ),
    ]