# Generated by Django 4.2.4 on 2023-10-18 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("business_model", "0004_equitydata_fuel_price_increase")]

    operations = [
        migrations.AlterField(
            model_name="businessmodel",
            name="model_name",
            field=models.CharField(
                choices=[
                    ("isolated_operator_led", "Isolated Mini-grid Company-led"),
                    ("isolated_cooperative_led", "Isolated Community-led"),
                    ("interconnected_operator_led", "Interconnected Mini-grid Company-led"),
                    ("interconnected_spv_led", "Interconnected DisCo-led"),
                    ("interconnected_cooperative_led", "Interconnected Community-led"),
                    ("interconnected_collaborative_spv_led", "Interconnected collaborative"),
                ],
                max_length=60,
                null=True,
            ),
        )
    ]