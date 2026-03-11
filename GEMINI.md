# City Clean

A Django-based waste management and reporting system for urban cleanliness.

## Project Overview

City Clean allows users to:
- Report illegal dumping (`denuncia`).
- Schedule waste collection (`agendamento`).
- Find recycling points (`PontoDeColeta`).
- Track requests through different statuses (Enviada, Em Análise, Aprovada, Concluída, Cancelada).

## Technical Stack

- **Framework:** Django 6.0.3
- **Language:** Python
- **Database:** SQLite (default)
- **Authentication:** Passwordless login using `django-sesame`.
- **Custom User:** `accounts.Usuario` (extends `AbstractUser`).
- **Locale:** `pt-br` (Brazilian Portuguese).
- **Timezone:** `America/Sao_Paulo`.

## Core Business Logic

- **Scheduling Limits:** Max 5 bookings (`Solicitacao`) per day (`MAX_BOOKINGS_PER_DAY = 5`).
- **Automatic Scheduling:**
  - `denuncia`: When status becomes `APROVADA`, it is automatically scheduled for the next available day.
  - `agendamento`: When status becomes `APROVADA`, it is scheduled for the `requested_date` provided by the user.
- **Audit:** Any change to `scheduled_date` must be logged in the `Reschedule` model.

## Domain Models

- **Material:** Types of recyclable materials (e.g., Plastic, Paper).
- **PontoDeColeta:** Locations where specific materials are accepted.
- **Solicitacao:** The main entity for reports and collection requests.
- **Reschedule:** Tracks history of date changes for collections.
- **Usuario:** Custom user model with a `telefone` field.

## Development Standards

- **Conventions:** Follow standard Django project structure and naming conventions.
- **Translations:** Keep user-facing strings in Brazilian Portuguese (`pt-br`).
- **Validation:** Always verify if a date is available before scheduling or rescheduling using `Solicitacao.is_date_available(date)`.
- **Integrity:** Ensure `Reschedule` records are created whenever `scheduled_date` is updated.
- **Types:** Use Django's `TextChoices` for status and request types.
- **Migrations:** Always create and run migrations for any model changes.
