# Generated by Django 3.2 on 2023-02-04 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FacilityType",
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
                ("facility_type", models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
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
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("date_start", models.DateTimeField()),
                ("date_end", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="UserType",
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
                    "user_type",
                    models.CharField(
                        choices=[
                            ("Household", "Household"),
                            ("Food", "Enterprise: Food"),
                            ("Retail", "Enterprise: Retail"),
                            ("Trades", "Enterprise: Trades"),
                            ("Digital", "Enterprise: Digital"),
                            ("Agricultural", "Enterprise: Agricultural"),
                            ("School", "Public facility: School"),
                            ("Mosque", "Public facility: Mosque"),
                            ("Church", "Public facility: Church"),
                            (
                                "Government building",
                                "Public facility: Government building",
                            ),
                            ("Town Hall", "Public facility: Town Hall"),
                            ("Health Center", "Health facility: Health Center"),
                            (
                                "Dispensary/Pharmacy",
                                "Health facility: Dispensary/Pharmacy",
                            ),
                            ("Clinic", "Health facility: Clinic"),
                            ("Hospital", "Health facility: Hospital"),
                        ],
                        max_length=120,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserGroup",
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
                    "tier",
                    models.CharField(
                        choices=[("Tier 1", "Tier 1"), ("Tier 2", "Tier 2")],
                        max_length=30,
                    ),
                ),
                ("number_users", models.IntegerField()),
                (
                    "facility_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cp_nigeria.facilitytype",
                    ),
                ),
                (
                    "user_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cp_nigeria.usertype",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="facilitytype",
            name="user_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="cp_nigeria.usertype"
            ),
        ),
    ]
