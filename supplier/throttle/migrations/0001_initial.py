# Generated by Django 4.1.1 on 2022-11-01 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ListModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "creater",
                    models.CharField(max_length=255, verbose_name="Who created"),
                ),
                ("openid", models.CharField(max_length=255, verbose_name="Openid")),
                (
                    "is_delete",
                    models.BooleanField(default=False, verbose_name="Delete Label"),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="Create Time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Update Time"
                    ),
                ),
                ("appid", models.CharField(max_length=255, verbose_name="Appid")),
                ("ip", models.CharField(max_length=32, verbose_name="IP")),
                ("method", models.CharField(max_length=18, verbose_name="Method")),
                (
                    "t_code",
                    models.CharField(max_length=255, verbose_name="Transaction Code"),
                ),
            ],
            options={
                "verbose_name": "data id",
                "verbose_name_plural": "data id",
                "db_table": "throttle",
                "ordering": ["-id"],
            },
        ),
    ]