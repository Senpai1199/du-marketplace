# Generated by Django 3.0.6 on 2020-05-16 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0018_auto_20200516_0633'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookset',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.UserProfile'),
        ),
    ]
