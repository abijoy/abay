# Generated by Django 4.2 on 2024-01-06 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_emailverificationcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverificationcode',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
