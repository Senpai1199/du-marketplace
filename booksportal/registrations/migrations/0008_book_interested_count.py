# Generated by Django 3.0.6 on 2020-05-13 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0007_auto_20200513_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='interested_count',
            field=models.SmallIntegerField(default=0),
        ),
    ]
