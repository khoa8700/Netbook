# Generated by Django 3.2.5 on 2022-01-25 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ebook', '0045_alter_novel_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='status',
            field=models.BooleanField(choices=[(True, 'Finished'), (False, 'In proccessing')], default=False),
        ),
    ]
