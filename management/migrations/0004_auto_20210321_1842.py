# Generated by Django 3.1.7 on 2021-03-21 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='photo',
            field=models.CharField(default=None, max_length=500),
        ),
    ]
