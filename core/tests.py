from django.test import TestCase
from django.utils import timezone
import datetime

from .models import Solicitacao, Reschedule


class SchedulingTests(TestCase):
    def setUp(self):
        self.today = datetime.date.today()

    def test_bookings_and_availability(self):
        # no bookings yet
        self.assertEqual(Solicitacao.bookings_count(self.today), 0)
        self.assertTrue(Solicitacao.is_date_available(self.today))

        # create MAX_BOOKINGS_PER_DAY solicitacoes scheduled for today
        for i in range(Solicitacao.MAX_BOOKINGS_PER_DAY):
            Solicitacao.objects.create(
                usuario=None,
                descricao=f"x{i}",
                foto="dummy.jpg",
                latitude=0,
                longitude=0,
                volume_estimado="1",
                status=Solicitacao.Status.ENVIADA,
                tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
                scheduled_date=self.today,
            )
        self.assertEqual(Solicitacao.bookings_count(self.today), Solicitacao.MAX_BOOKINGS_PER_DAY)
        self.assertFalse(Solicitacao.is_date_available(self.today))

    def test_next_available_day_and_available_days(self):
        # fill today, so next should be tomorrow
        for i in range(Solicitacao.MAX_BOOKINGS_PER_DAY):
            Solicitacao.objects.create(
                usuario=None,
                descricao="fill",
                foto="dummy.jpg",
                latitude=0,
                longitude=0,
                volume_estimado="1",
                status=Solicitacao.Status.ENVIADA,
                tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
                scheduled_date=self.today,
            )
        tomorrow = self.today + datetime.timedelta(days=1)
        self.assertEqual(Solicitacao.next_available_day(start_date=self.today), tomorrow)
        # available_days returns next few including tomorrow
        days = Solicitacao.available_days(start_date=self.today, count=3)
        self.assertIn(tomorrow, days)
        self.assertEqual(len(days), 3)

    def test_automatic_scheduling_for_denuncia(self):
        s = Solicitacao.objects.create(
            usuario=None,
            descricao="denunc",
            foto="dummy.jpg",
            latitude=0,
            longitude=0,
            volume_estimado="1",
            status=Solicitacao.Status.ENVIADA,
            tipo_solicitacao=Solicitacao.TipoSolicitacao.DENUNCIA,
        )
        # scheduled_date should still be None until approved
        self.assertIsNone(s.scheduled_date)
        s.status = Solicitacao.Status.APROVADA
        s.save()
        self.assertIsNotNone(s.scheduled_date)
        # ensure it's not today if today was full
        self.assertTrue(Solicitacao.is_date_available(s.scheduled_date))

    def test_reschedule_and_history(self):
        target_date = self.today + datetime.timedelta(days=2)
        s = Solicitacao.objects.create(
            usuario=None,
            descricao="agend",
            foto="dummy.jpg",
            latitude=0,
            longitude=0,
            volume_estimado="1",
            status=Solicitacao.Status.APROVADA,
            tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
            scheduled_date=self.today,
        )
        # reschedule to a new available date
        self.assertTrue(Solicitacao.is_date_available(target_date))
        s.reschedule(target_date)
        self.assertEqual(s.scheduled_date, target_date)
        self.assertEqual(s.reschedules.count(), 1)
        rec = s.reschedules.first()
        self.assertEqual(rec.old_date, self.today)
        self.assertEqual(rec.new_date, target_date)

        # make target_date full and try another reschedule
        for i in range(Solicitacao.MAX_BOOKINGS_PER_DAY):
            Solicitacao.objects.create(
                usuario=None,
                descricao="fill",
                foto="dummy.jpg",
                latitude=0,
                longitude=0,
                volume_estimado="1",
                status=Solicitacao.Status.ENVIADA,
                tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
                scheduled_date=target_date,
            )
        with self.assertRaises(ValueError):
            s.reschedule(target_date)
