# Generated by Django 3.2.18 on 2023-05-03 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0004_order_vat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='product_variation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
