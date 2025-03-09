# Generated by Django 5.1.6 on 2025-03-09 21:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("materials", "0004_alter_course_options_coursesubscription"),
        ("users", "0003_alter_user_managers"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="payment",
            options={"verbose_name": "Платеж", "verbose_name_plural": "Платежи"},
        ),
        migrations.AlterField(
            model_name="payment",
            name="amount",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="Сумма оплаты"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="materials.course",
                verbose_name="Курс",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="date",
            field=models.DateField(verbose_name="Дата оплаты"),
        ),
        migrations.AlterField(
            model_name="payment",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="materials.lesson",
                verbose_name="Урок",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_method",
            field=models.CharField(
                choices=[("cash", "Наличные"), ("card", "Карта")],
                max_length=20,
                verbose_name="Способ оплаты",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
