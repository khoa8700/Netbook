# Generated by Django 4.0 on 2022-02-10 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0059_alter_tag_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
