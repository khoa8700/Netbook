# Generated by Django 4.0 on 2022-02-10 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0055_remove_bookmark_recently_chapter_once_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='hobby',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='job',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
