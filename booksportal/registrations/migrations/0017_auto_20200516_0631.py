# Generated by Django 3.0.6 on 2020-05-16 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0016_bookset_interested_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookset',
            name='contains_books',
        ),
        migrations.RemoveField(
            model_name='bookset',
            name='contains_readings',
        ),
        migrations.AddField(
            model_name='book',
            name='ineterested_users',
            field=models.ManyToManyField(related_name='books_wishlist', to='registrations.UserProfile'),
        ),
        migrations.AddField(
            model_name='bookset',
            name='ineterested_users',
            field=models.ManyToManyField(related_name='booksets_wishlist', to='registrations.UserProfile'),
        ),
    ]
