# Generated by Django 4.1.1 on 2023-01-24 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_user_bio"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="parent_mobile",
            field=models.CharField(
                blank=True, max_length=15, null=True, verbose_name="Parent Mobile"
            ),
        ),
    ]