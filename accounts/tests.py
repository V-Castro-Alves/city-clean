from django.test import TestCase

from .models import Usuario


class CadastroViewTests(TestCase):
	def setUp(self):
		self.existing_user = Usuario.objects.create_user(
			username="existente@example.com",
			email="existente@example.com",
			password="testpass123",
			first_name="Existente",
			last_name="Usuario",
			cpf="10987654321",
			telefone="47999999999",
			endereco="Rua Exemplo, 10",
		)

	def test_cadastro_view_rejeita_campos_obrigatorios_vazios(self):
		response = self.client.post(
			"/accounts/cadastro/",
			data={
				"first_name": "",
				"last_name": "",
				"email": "",
				"cpf": "",
				"telefone": "",
				"endereco": "",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["error"], "Todos os campos marcados com * são obrigatórios.")
		print(
			f"[CADASTRO] status_code={response.status_code} | error={response.context['error']}"
		)
