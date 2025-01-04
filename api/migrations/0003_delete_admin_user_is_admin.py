# Generated by Django 5.1.3 on 2024-12-22 06:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_user"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Admin",
        ),
        migrations.AddField(
            model_name="user",
            name="is_admin",
            field=models.BooleanField(default=False),
        ),
    ]