# Generated by Django 5.1.3 on 2025-01-02 06:36

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_delete_customuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, 'Rating cannot be negative'), django.core.validators.MaxValueValidator(5.0, 'Rating cannot exceed 5.0')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='restaurant.restaurant')),
            ],
        ),
    ]
