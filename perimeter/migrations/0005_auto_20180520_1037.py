from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("perimeter", "0004_auto_20170407_0639")]

    operations = [
        migrations.AlterField(
            model_name="accesstokenuse",
            name="client_user_agent",
            field=models.TextField(blank=True, verbose_name="Client User Agent"),
        )
    ]
