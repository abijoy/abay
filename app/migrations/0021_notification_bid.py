# Generated by Django 4.2 on 2024-01-22 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_rename_notificatin_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='bid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.auction'),
        ),
    ]
