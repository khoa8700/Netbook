# Generated by Django 4.0 on 2022-02-09 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0053_userinfo_avatar_alter_novel_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NovelTag',
        ),
    ]
