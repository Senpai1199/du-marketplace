# Generated by Django 3.0.6 on 2020-05-16 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0021_auto_20200516_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='registrations.Course'),
            preserve_default=False,
        ),
    ]
