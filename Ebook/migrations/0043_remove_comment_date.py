# Generated by Django 3.2.5 on 2022-01-23 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0042_alter_comment_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='date',
        ),
    ]
