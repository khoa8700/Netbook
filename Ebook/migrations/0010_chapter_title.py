# Generated by Django 3.2.5 on 2021-12-31 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0009_auto_20211230_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
