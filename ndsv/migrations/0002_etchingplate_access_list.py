# Generated by Django 3.1.1 on 2020-09-29 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndsv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='etchingplate',
            name='access_list',
            field=models.JSONField(default=list),
        ),
    ]
