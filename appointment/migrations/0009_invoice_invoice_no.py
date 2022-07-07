# Generated by Django 4.0.3 on 2022-05-06 15:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0008_remove_invoice_due_amount_remove_invoice_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_no',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
