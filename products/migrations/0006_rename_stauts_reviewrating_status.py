# Generated by Django 3.2.18 on 2023-05-03 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_reviewrating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewrating',
            old_name='stauts',
            new_name='status',
        ),
    ]
