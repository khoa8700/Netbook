# Generated by Django 3.2.5 on 2022-01-28 09:42

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0048_alter_chapter_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='address',
            new_name='hobby',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='job',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='self_introduction',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
