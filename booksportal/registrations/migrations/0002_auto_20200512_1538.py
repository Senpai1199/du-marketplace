# Generated by Django 3.0.6 on 2020-05-12 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('B', 'Book'), ('N', 'Note'), ('R', 'Reading')], default='S', max_length=1),
        ),
        migrations.AddField(
            model_name='book',
            name='course',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='book',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='book',
            name='edition',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='book',
            name='sold',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
