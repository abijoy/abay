# Generated by Django 4.2 on 2024-01-22 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_notification_description_alter_notification_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='notification_type',
            new_name='type',
        ),
    ]
