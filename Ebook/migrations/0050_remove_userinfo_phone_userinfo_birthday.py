# Generated by Django 4.0 on 2022-02-07 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0049_auto_20220128_1642'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='phone',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='birthday',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
