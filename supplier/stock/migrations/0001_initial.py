# Generated by Django 4.1.1 on 2022-11-01 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StockRecord",
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
                (
                    "goods_id",
                    models.PositiveIntegerField(
                        verbose_name="goods id of stock record"
                    ),
                ),
                (
                    "goods_code",
                    models.CharField(
                        db_index=True, max_length=255, verbose_name="Goods Code"
                    ),
                ),
                (
                    "goods_image",
                    models.CharField(
                        blank=True,
                        max_length=1024,
                        null=True,
                        verbose_name="Goods Image Url",
                    ),
                ),
                (
                    "stock_id",
                    models.PositiveIntegerField(
                        verbose_name="stock id of stock record"
                    ),
                ),
                ("stock_qty", models.IntegerField(default=0, verbose_name="stock qty")),
                (
                    "stock_status",
                    models.IntegerField(
                        choices=[
                            (-1, "Damage Stock"),
                            (0, "PrePurchase Stock"),
                            (1, "Purchased Stock"),
                            (2, "Sorted Stock"),
                            (3, "In Stock"),
                        ],
                        default=None,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "stock_record",
                "verbose_name_plural": "Stock Record",
                "db_table": "stock_record",
                "ordering": ["-id"],
            },
        ),
    ]
