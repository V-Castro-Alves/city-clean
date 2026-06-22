import datetime
import shutil
import tempfile
from io import BytesIO
from unittest import mock

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import Usuario

from .forms import AgendamentoForm, DenunciaForm, SolicitacaoForm
from .models import Material, Solicitacao


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="city_clean_test_media_")


def make_test_image(name="test.png", color=(255, 0, 0)):
	image = Image.new("RGB", (1, 1), color)
	buffer = BytesIO()
	image.save(buffer, format="PNG")
	return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CoreRuleTests(TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.addClassCleanup(shutil.rmtree, TEST_MEDIA_ROOT, ignore_errors=True)

	def setUp(self):
		self.user = Usuario.objects.create_user(
			username="teste@example.com",
			email="teste@example.com",
			password="testpass123",
			first_name="Teste",
			last_name="Usuario",
			cpf="12345678901",
			telefone="47999999999",
			endereco="Rua Teste, 123",
		)
		self.material = Material.objects.create(nome="Metal")

	def _base_form_data(self):
		return {
			"descricao": "Resíduo encontrado na rua",
			"materiais": [self.material.pk],
			"volume_estimado": "1 saco",
			"latitude": "-26.300000",
			"longitude": "-48.850000",
		}

	def test_denuncia_form_rejeita_localizacao_fora_da_area(self):
		form = DenunciaForm(
			data={**self._base_form_data(), "latitude": "-27.000000"},
			files={"foto": make_test_image()},
		)

		self.assertFalse(form.is_valid())
		self.assertIn("Localização fora da área de atendimento.", form.non_field_errors())
		print(
			f"[DENUNCIA] is_valid={form.is_valid()} | error={list(form.non_field_errors())}"
		)

	def test_agendamento_form_rejeita_data_indisponivel(self):
		requested_date = datetime.date.today() + datetime.timedelta(days=2)

		with mock.patch.object(Solicitacao, "available_days", return_value=[requested_date]), \
			mock.patch.object(Solicitacao, "is_date_available", return_value=False):
			invalid_form = AgendamentoForm(
				data={
					"descricao": "Coleta de eletrodomésticos",
					"materiais": [self.material.pk],
					"volume_estimado": "2 itens",
					"requested_date": str(requested_date),
					"latitude": "-26.300000",
					"longitude": "-48.850000",
				},
				files={"foto": make_test_image()},
			)
			self.assertFalse(invalid_form.is_valid())
			self.assertIn("A data selecionada não está mais disponível.", invalid_form.errors["requested_date"])
			print(
				f"[AGENDAMENTO] requested_date={requested_date} | is_valid={invalid_form.is_valid()} | error={list(invalid_form.errors['requested_date'])}"
			)

	def test_solicitacao_form_exige_data_para_agendamento(self):
		form = SolicitacaoForm(
			data={
				"descricao": "Solicitação de coleta",
				"materiais": [self.material.pk],
				"tipo_solicitacao": Solicitacao.TipoSolicitacao.AGENDAMENTO,
				"requested_date": "",
			},
			files={"foto": make_test_image()},
		)

		self.assertFalse(form.is_valid())
		self.assertIn("A date is required for pickup requests.", form.non_field_errors())
		print(
			f"[SOLICITACAO FORM] tipo=agendamento | is_valid={form.is_valid()} | error={list(form.non_field_errors())}"
		)

	def test_solicitacao_can_cancel_obedece_regra_de_2_dias(self):
		solicitacao = Solicitacao(
			usuario=self.user,
			descricao="Agendamento",
			foto=make_test_image(),
			tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
			requested_date=datetime.date.today() + datetime.timedelta(days=2),
			latitude="-26.300000",
			longitude="-48.850000",
			volume_estimado="1 item",
			status=Solicitacao.Status.ENVIADA,
		)

		self.assertTrue(solicitacao.can_cancel)
		print(
			f"[CAN_CANCEL] status={solicitacao.status} | requested_date={solicitacao.requested_date} | can_cancel={solicitacao.can_cancel}"
		)

	def test_is_date_available_fica_false_quando_atinge_limite(self):
		target_date = datetime.date.today() + datetime.timedelta(days=10)

		for index in range(Solicitacao.MAX_BOOKINGS_PER_DAY):
			Solicitacao.objects.create(
				usuario=self.user,
				descricao=f"Solicitacao {index}",
				foto=make_test_image(name=f"test_{index}.png"),
				tipo_solicitacao=Solicitacao.TipoSolicitacao.AGENDAMENTO,
				requested_date=target_date,
				scheduled_date=target_date,
				latitude="-26.300000",
				longitude="-48.850000",
				volume_estimado="1 item",
			)

		self.assertFalse(Solicitacao.is_date_available(target_date))
		print(
			f"[DATE AVAILABILITY] date={target_date} | max_per_day={Solicitacao.MAX_BOOKINGS_PER_DAY} | available={Solicitacao.is_date_available(target_date)}"
		)
