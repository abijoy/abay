# Generated by Django 4.2 on 2024-01-07 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_remove_emailverificationcode_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverificationcode',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
