# Generated by Django 2.0.5 on 2018-08-22 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0002_sponsor_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='year',
            field=models.IntegerField(default=2018),
        ),
    ]
