# Generated by Django 3.2.5 on 2022-01-20 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0037_novel_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
