# Generated by Django 2.0.2 on 2020-05-31 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='this is description'),
            preserve_default=False,
        ),
    ]
