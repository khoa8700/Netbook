# Generated by Django 3.2.5 on 2022-01-03 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0020_rating_rating_once'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.CheckConstraint(check=models.Q(('rate__range', (0, 5))), name='valid_rate'),
        ),
    ]
