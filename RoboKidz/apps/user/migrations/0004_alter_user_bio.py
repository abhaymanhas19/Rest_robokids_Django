# Generated by Django 4.1.1 on 2023-01-04 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_alter_user_poc_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="bio",
            field=models.TextField(blank=True, verbose_name="Bio"),
        ),
    ]
