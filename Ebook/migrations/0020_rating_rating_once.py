# Generated by Django 3.2.5 on 2022-01-03 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0019_auto_20220103_2047'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('user', 'novel'), name='rating_once'),
        ),
    ]
