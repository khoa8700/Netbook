# Generated by Django 3.2.5 on 2021-12-31 08:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0015_tag_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='slug',
        ),
    ]
