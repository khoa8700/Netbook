# Generated by Django 3.2.5 on 2022-01-20 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0036_alter_chapter_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
