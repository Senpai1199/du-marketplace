# Generated by Django 3.0.6 on 2020-05-15 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0015_auto_20200515_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookset',
            name='interested_count',
            field=models.SmallIntegerField(default=0),
        ),
    ]
