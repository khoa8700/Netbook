# Generated by Django 3.2.5 on 2021-12-31 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0010_chapter_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='slug',
            field=models.SlugField(default='', unique=True),
            preserve_default=False,
        ),
    ]