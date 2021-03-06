# Generated by Django 2.0.5 on 2018-08-16 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mentor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('contact', models.TextField(blank=True, max_length=13, null=True)),
                ('email', models.CharField(max_length=256)),
                ('detail', models.TextField()),
                ('description', models.TextField()),
                ('profile_pic', models.ImageField(upload_to='static/uploads/mentors')),
                ('flag', models.BooleanField(default=False)),
            ],
        ),
    ]
