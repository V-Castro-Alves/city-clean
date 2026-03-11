import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_solicitacao_foto_opcional"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacao",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
