# Generated by Django 3.1.1 on 2020-09-29 16:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndsv', '0002_etchingplate_access_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etchingplate',
            name='beam_id',
            field=models.CharField(max_length=36, unique=True, validators=[django.core.validators.MinLengthValidator(36)]),
        ),
    ]
