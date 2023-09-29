# Generated by Django 4.2.4 on 2023-09-26 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("projects", "0020_alter_economicdata_currency")]

    operations = [
        migrations.CreateModel(
            name="BMQuestion",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_for_user", models.TextField()),
                ("criteria", models.TextField()),
                ("criteria_weight", models.FloatField(verbose_name="Criteria weight")),
                ("score_allowed_values", models.TextField(null=True)),
                ("weighted_score", models.FloatField(null=True, verbose_name="Weighted Score")),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("dialogue", "Engagement, dialogue, and co-determination"),
                            ("steering", "Steering capacities"),
                            ("control", "Asserting control and credibility"),
                            ("institutional", "Supporting Institutional structures"),
                            ("economic", "Potential for economic co-benefits"),
                            ("financial", "Financial capacities"),
                        ],
                        max_length=60,
                        null=True,
                    ),
                ),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="BusinessModel",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "grid_condition",
                    models.CharField(
                        blank=True,
                        choices=[("interconnected", "Interconnected"), ("isolated", "Isolated")],
                        default=False,
                        max_length=14,
                        null=True,
                    ),
                ),
                ("decision_tree", models.TextField(blank=True, null=True)),
                (
                    "model_name",
                    models.CharField(
                        choices=[
                            ("isolated_operator_led", "isolated operator led"),
                            ("isolated_cooperative_led", "isolated cooperative led"),
                            ("isolated_split_asset", "isolated split asset"),
                            ("interconnected_operator_led", "interconnected operator led"),
                            ("interconnected_spv_led", "interconnected spv led"),
                            ("interconnected_cooperative_led", "interconnected cooperative led"),
                            ("interconnected_collaborative_spv_led", "interconnected collaborative spv led"),
                        ],
                        max_length=60,
                        null=True,
                    ),
                ),
                (
                    "scenario",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="projects.scenario"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BMAnswer",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.FloatField(null=True, verbose_name="Score")),
                (
                    "business_model",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_answers",
                        to="business_model.businessmodel",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to="business_model.bmquestion"
                    ),
                ),
            ],
        ),
    ]
