# city-clean

Sistema web para solicitação de coleta de resíduos e registro de denúncias de descarte irregular, desenvolvido com Django.

## Pré-requisitos

- Python 3.11+
- pip

## Instalação

1. Clone o repositório e entre na pasta do projeto:

```bash
git clone <url-do-repositorio>
cd city-clean
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Aplique as migrações do banco de dados:

```bash
python manage.py migrate
```

5. (Opcional) Crie um superusuário para acessar o painel administrativo:

```bash
python manage.py createsuperuser
```

## Executando o servidor

```bash
python manage.py runserver
```

O servidor estará disponível em [http://127.0.0.1:8000](http://127.0.0.1:8000).

Para rodar em um endereço e porta específicos (ex: acessível na rede local):

```bash
python manage.py runserver 0.0.0.0:8000
```
