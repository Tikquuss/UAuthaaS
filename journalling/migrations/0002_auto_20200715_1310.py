# Generated by Django 3.0.8 on 2020-07-15 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journalling', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='record',
            field=models.CharField(max_length=254),
        ),
    ]
