# Generated by Django 3.2.5 on 2022-01-03 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0018_auto_20220103_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='avg_rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='novel',
            name='nunber_rating',
            field=models.IntegerField(default=0),
        ),
    ]
