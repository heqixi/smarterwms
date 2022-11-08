# Generated by Django 4.1.1 on 2022-11-02 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_alter_storemodel_merchant"),
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
    ]
