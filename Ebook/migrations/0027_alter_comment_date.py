# Generated by Django 3.2.5 on 2022-01-08 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0026_alter_comment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]