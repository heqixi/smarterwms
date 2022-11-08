# Generated by Django 4.1.1 on 2022-11-03 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0011_alter_storemodel_merchant"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storemodel",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={
                    models.SmallIntegerField(
                        db_index=True, verbose_name="Store Type"
                    ): 1
                },
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="store.storemodel",
            ),
        ),
        migrations.AlterField(
            model_name="storeproductmodel",
            name="brand_id",
            field=models.IntegerField(default=0, verbose_name="Store product brand id"),
        ),
        migrations.AlterField(
            model_name="storeproductmodel",
            name="brand_name",
            field=models.CharField(
                max_length=100, null=True, verbose_name="Store product brand name"
            ),
        ),
        migrations.AlterField(
            model_name="storeproductmodel",
            name="category_id",
            field=models.IntegerField(
                default=0, verbose_name="Store product thumbnail url"
            ),
        ),
        migrations.AlterField(
            model_name="storeproductmodel",
            name="days_to_ship",
            field=models.SmallIntegerField(
                default=3, verbose_name="Store product days to ship"
            ),
        ),
        migrations.AlterField(
            model_name="storeproductmodel",
            name="weight",
            field=models.FloatField(null=True, verbose_name="Store product weight"),
        ),
    ]
