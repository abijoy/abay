# Generated by Django 3.2.3 on 2021-06-05 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_product_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='auc_end_time',
            field=models.DateTimeField(verbose_name='Bid Ends at '),
        ),
    ]
