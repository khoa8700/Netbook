# Generated by Django 4.0 on 2022-02-09 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0054_delete_noveltag'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bookmark',
            name='recently_chapter_once',
        ),
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(fields=('user', 'novel', 'number'), name='read_chapter'),
        ),
    ]