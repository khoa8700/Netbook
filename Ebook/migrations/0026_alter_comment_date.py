# Generated by Django 3.2.5 on 2022-01-08 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0025_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
