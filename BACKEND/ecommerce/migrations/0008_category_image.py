# Generated by Django 4.2.4 on 2023-10-06 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0007_alter_cart_client_alter_cart_date_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories', verbose_name='imagen'),
        ),
    ]
