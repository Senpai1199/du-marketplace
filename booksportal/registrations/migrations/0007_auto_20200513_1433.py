# Generated by Django 3.0.6 on 2020-05-13 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0006_auto_20200513_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(default='default_male_dp.jpeg', upload_to='profile_pics'),
        ),
    ]
