# Generated by Django 5.0.1 on 2024-02-17 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_alter_wallet_balance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='amount',
            field=models.FloatField(),
        ),
    ]
