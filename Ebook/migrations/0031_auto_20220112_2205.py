# Generated by Django 3.2.5 on 2022-01-12 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0030_rename_ee_novel_number_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='ban_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='prev_ban_level',
            field=models.IntegerField(default=0),
        ),
    ]
