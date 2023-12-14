# Generated by Django 3.2.3 on 2021-06-05 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_product_auc_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='min_bid_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Minimum Bidding Price'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Product Name'),
        ),
    ]
