# Generated by Django 4.0.3 on 2022-05-06 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0007_invoice_invoice_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='due_amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='paid_amount',
        ),
    ]
