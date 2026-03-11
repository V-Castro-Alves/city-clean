from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_solicitacao_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacao",
            name="foto2",
            field=models.ImageField(blank=True, upload_to="solicitacoes/"),
        ),
        migrations.AddField(
            model_name="solicitacao",
            name="foto3",
            field=models.ImageField(blank=True, upload_to="solicitacoes/"),
        ),
        migrations.AlterField(
            model_name="solicitacao",
            name="volume_estimado",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
