# Generated by Django 3.2.5 on 2021-12-29 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0006_alter_novel_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='tags',
            field=models.ManyToManyField(to='Ebook.Tag'),
        ),
        migrations.AlterField(
            model_name='novel',
            name='thumbnail',
            field=models.ImageField(blank=True, default='placeholder.png', null=True, upload_to='images/'),
        ),
    ]
