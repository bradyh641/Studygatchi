from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("quickstart", "0003_merge_20260728_2227"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProhibitedSite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hostname", models.CharField(max_length=253)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="quickstart.studyuser",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="prohibitedsite",
            constraint=models.UniqueConstraint(
                fields=("user", "hostname"),
                name="unique_prohibited_site_per_user",
            ),
        ),
    ]
