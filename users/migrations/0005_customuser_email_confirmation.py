# Generated by Django 5.0.1 on 2024-01-05 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email_confirmation',
            field=models.BooleanField(default=False),
        ),
    ]
