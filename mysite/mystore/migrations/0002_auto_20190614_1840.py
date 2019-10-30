# Generated by Django 2.2 on 2019-06-14 23:40

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.DecimalField(decimal_places=0, max_digits=10, verbose_name='Telefono'),
        ),
        migrations.AlterField(
            model_name='order',
            name='due_date',
            field=models.DateField(default=datetime.datetime(2019, 6, 29, 18, 40, 1, 605158), verbose_name='Fecha de entrega'),
        ),
    ]
