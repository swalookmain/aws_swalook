# Generated migration to remove opening_time and closing_time from SalonBranch
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('_api_', '0009_vendorinvoice_coupon_points_used'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salonbranch',
            name='opening_time',
        ),
        migrations.RemoveField(
            model_name='salonbranch',
            name='closing_time',
        ),
    ]
