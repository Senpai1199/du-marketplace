# Generated by Django 3.0.6 on 2020-05-16 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0020_auto_20200516_0717'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='ineterested_users',
            new_name='interested_users',
        ),
    ]