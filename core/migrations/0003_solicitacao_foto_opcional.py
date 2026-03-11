from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_seed_pontos_coleta"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solicitacao",
            name="foto",
            field=models.ImageField(upload_to="solicitacoes/"),
        ),
    ]
