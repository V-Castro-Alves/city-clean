from django.db import models
from django.conf import settings

class Material(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

''
class PontoDeColeta(models.Model):
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    materiais_aceitos = models.ManyToManyField(Material, blank=True)

    def __str__(self):
        return self.nome


class Solicitacao(models.Model):
    # business rules constants
    MAX_BOOKINGS_PER_DAY = 5

    class Status(models.TextChoices):
        ENVIADA = 'enviada', 'Enviada'
        EM_ANALISE = 'em_analise', 'Em Análise'
        APROVADA = 'aprovada', 'Aprovada'
        CONCLUIDA = 'concluida', 'Concluída'
        CANCELADA = 'cancelada', 'Cancelada'

    class TipoSolicitacao(models.TextChoices):
        NAO_ESPECIFICADO = 'nao_especificado', 'Não Especificado'
        DENUNCIA = 'denuncia', 'Denúncia'
        AGENDAMENTO = 'agendamento', 'Agendamento'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )

    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='solicitacoes/')
    materiais = models.ManyToManyField(Material, blank=True)
    tipo_solicitacao = models.CharField(max_length=20, choices=TipoSolicitacao, default=TipoSolicitacao.NAO_ESPECIFICADO)

    # date requested by user (agendamento only)
    requested_date = models.DateField(blank=True, null=True)
    # date that has been or will be performed
    scheduled_date = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status, default=Status.ENVIADA)
    motivo_cancelamento = models.TextField(blank=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    volume_estimado = models.CharField(max_length=100)

    def __str__(self):
        parts = [f"{self.__class__.__name__} #{self.pk}", self.status]
        if self.scheduled_date:
            parts.append(f"on {self.scheduled_date}")
        return " — ".join(parts)

    # ----- scheduling helpers -----
    @classmethod
    def bookings_count(cls, date):
        return cls.objects.filter(scheduled_date=date).count()

    @classmethod
    def is_date_available(cls, date):
        return cls.bookings_count(date) < cls.MAX_BOOKINGS_PER_DAY

    @classmethod
    def next_available_day(cls, start_date=None):
        import datetime

        if start_date is None:
            start_date = datetime.date.today()
        current = start_date
        while True:
            if cls.is_date_available(current):
                return current
            current += datetime.timedelta(days=1)

    @classmethod
    def available_days(cls, start_date=None, count=5):
        days = []
        if start_date is None:
            import datetime

            start_date = datetime.date.today()
        current = start_date
        while len(days) < count:
            if cls.is_date_available(current):
                days.append(current)
            import datetime

            current += datetime.timedelta(days=1)
        return days

    def reschedule(self, new_date):
        if not self.is_date_available(new_date):
            raise ValueError("Date not available for scheduling")
        old = self.scheduled_date
        self.scheduled_date = new_date
        self.save(update_fields=['scheduled_date'])
        Reschedule.objects.create(solicitacao=self, old_date=old, new_date=new_date)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            orig = Solicitacao.objects.filter(pk=self.pk).first()
            if orig:
                old_status = orig.status
        super().save(*args, **kwargs)

        # automatic scheduling for denúncias when approved
        if (
            self.tipo_solicitacao == self.TipoSolicitacao.DENUNCIA
            and self.status == self.Status.APROVADA
            and self.scheduled_date is None
        ):
            # schedule to next available day
            self.scheduled_date = self.next_available_day()
            super().save(update_fields=['scheduled_date'])

        # for agendamentos, when approved set scheduled_date to requested_date
        if (
            self.tipo_solicitacao == self.TipoSolicitacao.AGENDAMENTO
            and self.status == self.Status.APROVADA
            and self.requested_date
            and self.scheduled_date is None
        ):
            self.scheduled_date = self.requested_date
            super().save(update_fields=['scheduled_date'])


# keep track of reschedules for audit
class Reschedule(models.Model):
    solicitacao = models.ForeignKey(
        Solicitacao,
        on_delete=models.CASCADE,
        related_name='reschedules'
    )
    old_date = models.DateField()
    new_date = models.DateField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reschedule of {self.solicitacao} from {self.old_date} to {self.new_date}"
