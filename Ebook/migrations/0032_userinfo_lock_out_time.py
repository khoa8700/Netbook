# Generated by Django 3.2.5 on 2022-01-13 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0031_auto_20220112_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='lock_out_time',
            field=models.DateTimeField(null=True),
        ),
    ]
