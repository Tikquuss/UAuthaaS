# Generated by Django 3.0.7 on 2020-06-24 09:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users_crud', '0003_auto_20200623_0151'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofil',
            name='keycloak_id',
            field=models.CharField(default=uuid.uuid4, max_length=255),
        ),
    ]
