# Generated by Django 3.2.3 on 2021-06-02 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_auction_placed_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='documents/%Y/%m/%d'),
        ),
    ]