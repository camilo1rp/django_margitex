# Generated by Django 2.2 on 2019-06-19 02:48

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystore', '0006_auto_20190618_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2019, 7, 3, 21, 48, 26, 6170), verbose_name='Fecha de entrega'),
        ),
    ]
