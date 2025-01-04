# Generated by Django 5.1.3 on 2024-12-23 07:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0005_alter_log_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="user",
            name="nickname",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=15,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        "^\\+?1?\\d{9,15}$", "请输入有效的手机号。"
                    )
                ],
            ),
        ),
    ]