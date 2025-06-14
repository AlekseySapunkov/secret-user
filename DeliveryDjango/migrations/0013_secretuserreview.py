# Generated by Django 5.0.6 on 2024-06-02 21:23

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DeliveryDjango', '0012_person_is_secret'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecretUserReview',
            fields=[
                ('review_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='DeliveryDjango.review')),
                ('problem_description', models.TextField(blank=True, help_text='Описание проблемы')),
                ('improvement_suggestions', models.TextField(blank=True, help_text='Предложения по улучшению')),
                ('delivery_quality_rating', models.IntegerField(blank=True, help_text='Оценка качества доставки', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('overall_experience_rating', models.IntegerField(blank=True, help_text='Общая оценка опыта', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
            options={
                'verbose_name': 'Скрытый отзыв пользователя',
                'verbose_name_plural': 'Скрытые отзывы пользователей',
            },
            bases=('DeliveryDjango.review',),
        ),
    ]
