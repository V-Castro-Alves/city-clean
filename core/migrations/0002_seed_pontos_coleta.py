from django.db import migrations


MATERIAIS = [
    "Recicláveis",
    "Eletrônicos",
    "Móveis/Entulho",
    "Óleo",
    "Orgânicos",
]

PONTOS = [
    {
        "nome": "Ecoponto Centro",
        "endereco": "R. Dr. João Colin, 100 — Centro, Joinville/SC",
        "horario": "Seg–Sex 08h–17h, Sáb 08h–12h",
        "latitude": "-26.304400",
        "longitude": "-48.848700",
        "materiais": ["Recicláveis", "Eletrônicos"],
    },
    {
        "nome": "Ecoponto Bucarein",
        "endereco": "Av. Getúlio Vargas, 500 — Bucarein, Joinville/SC",
        "horario": "Seg–Sex 08h–18h",
        "latitude": "-26.298500",
        "longitude": "-48.841200",
        "materiais": ["Recicláveis", "Óleo"],
    },
    {
        "nome": "Ecoponto Costa e Silva",
        "endereco": "R. Araranguá, 800 — Costa e Silva, Joinville/SC",
        "horario": "Seg–Sáb 07h–17h",
        "latitude": "-26.322000",
        "longitude": "-48.856000",
        "materiais": ["Móveis/Entulho", "Recicláveis"],
    },
    {
        "nome": "Ponto de Coleta Floresta",
        "endereco": "R. Blumenau, 200 — Floresta, Joinville/SC",
        "horario": "Seg–Sex 08h–17h",
        "latitude": "-26.293000",
        "longitude": "-48.862000",
        "materiais": ["Eletrônicos", "Recicláveis"],
    },
    {
        "nome": "Ecoponto Iririú",
        "endereco": "R. São Paulo, 400 — Iririú, Joinville/SC",
        "horario": "Ter–Sáb 08h–17h",
        "latitude": "-26.276000",
        "longitude": "-48.856000",
        "materiais": ["Óleo", "Recicláveis", "Orgânicos"],
    },
]


def seed_data(apps, schema_editor):
    Material = apps.get_model("core", "Material")
    PontoDeColeta = apps.get_model("core", "PontoDeColeta")

    materiais_map = {}
    for nome in MATERIAIS:
        m, _ = Material.objects.get_or_create(nome=nome)
        materiais_map[nome] = m

    for data in PONTOS:
        ponto, created = PontoDeColeta.objects.get_or_create(
            nome=data["nome"],
            defaults={
                "endereco": data["endereco"],
                "horario": data["horario"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
            },
        )
        if created:
            for nome in data["materiais"]:
                ponto.materiais_aceitos.add(materiais_map[nome])


def unseed_data(apps, schema_editor):
    Material = apps.get_model("core", "Material")
    PontoDeColeta = apps.get_model("core", "PontoDeColeta")
    nomes_pontos = [p["nome"] for p in PONTOS]
    PontoDeColeta.objects.filter(nome__in=nomes_pontos).delete()
    Material.objects.filter(nome__in=MATERIAIS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]
