# Generated by Django 3.2.5 on 2022-01-03 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0021_rating_valid_rate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='novel',
            old_name='nunber_rating',
            new_name='number_rating',
        ),
    ]
