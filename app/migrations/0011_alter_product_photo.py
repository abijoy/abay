# Generated by Django 3.2.3 on 2021-06-03 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_product_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(blank=True, default='default.png', null=True, upload_to='uploads/%Y-%m-%d'),
        ),
    ]
