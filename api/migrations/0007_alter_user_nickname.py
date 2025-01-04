# Generated by Django 5.1.3 on 2024-12-23 07:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_user_email_user_nickname_user_phone_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(
                blank=True,
                default=models.CharField(max_length=150, unique=True),
                max_length=50,
                null=True,
            ),
        ),
    ]
