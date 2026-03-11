## Plan: City-Clean Full Implementation

**TL;DR:** The project has a solid data model and scheduling logic but is missing the authentication layer, public-facing pages, the map, and all visual design. The reference site at urban-sort-buddy guides the frontend layout. Bootstrap 5 + Leaflet.js were chosen as the UI stack.

---

### Phase 1 — Critical Fixes (unblock the app)

1. **Create `accounts/urls.py`** — the main URL conf already imports it; missing file crashes the entire site
2. **Run `makemigrations` + `migrate`** — no migrations exist, DB has no tables yet
3. **Register `Usuario` in admin.py** — currently omitted
4. **Add `Pillow`** to requirements.txt — needed for `ImageField` and image compression

---

### Phase 2 — Model Changes

5. Add `cpf` (CharField 14) and `endereco` (CharField 300) to `Usuario` in models.py — reference site register form has these
6. Add `horario` (CharField 100) to `PontoDeColeta` in models.py — reference site shows operating hours per point
7. Fix `SESAME_MAX_AGE` from 600s → 900s in settings.py to match RNF04 (15 min)
8. Add bounding box constants to settings.py: `SERVICE_AREA_LAT_MIN/MAX`, `SERVICE_AREA_LNG_MIN/MAX` for RF05 geographic validation
9. Add image compression to `Solicitacao.save()` using Pillow: compress uploaded photo to JPEG 80% quality, max 2MB (RF03)
10. Re-run `makemigrations` + `migrate`

---

### Phase 3 — Backend: Authentication (accounts app)

11. **views.py — `login_view`**: renders email form; POST → finds user by email → sends magic link via console email backend
12. **views.py — `cadastro_view`**: renders registration form; POST → creates `Usuario` → auto-sends magic link to log them in
13. **Sesame verification**: wire sesame's built-in token view at `accounts/auth/` for the magic link redirect
14. **views.py — `logout_view`**: `auth.logout()` + redirect to home
15. **`accounts/urls.py`** *(create)*: routes for `login/`, `cadastro/`, `logout/`, `auth/<token>/` (sesame)

---

### Phase 4 — Backend: Core Views, Forms & URLs

16. **views.py — `home_view`**: public, no login required
17. **views.py — `pontos_descarte_view`**: public; passes all `PontoDeColeta` objects + serialized JSON for Leaflet markers
18. **views.py — `denuncia_create_view`**: `@login_required`; uses a `DenunciaForm`; validates photo + location required (RN01); sends confirmation email (RF08)
19. **views.py — `agendamento_create_view`**: `@login_required`; uses `AgendamentoForm`; min date = today + 2 days (RN02); sends confirmation email (RF08)
20. **forms.py — `DenunciaForm`**: fields: descricao, foto, latitude, longitude; bounding box validator on lat/lng (RF05)
21. **forms.py — `AgendamentoForm`**: fields: descricao, volume_estimado, requested_date (choices from `available_days(today+2)`); bounding box validator
22. **views.py — `faq_view`**: public; static FAQ content about waste types (RF10)
23. **urls.py** update routes: `/` (home), `/pontos-descarte/`, `/denuncia/`, `/solicitar-coleta/`, `/minhas-solicitacoes/`, `/solicitacao/<pk>/`, `/duvidas-frequentes/`

---

### Phase 5 — Frontend: Base Template

24. **`core/templates/base.html`** *(create)*: Bootstrap 5 CDN, responsive navbar — logo "CityClean", nav links (Pontos de Descarte, Solicitar Coleta, Denúncia), auth area (Entrar + Cadastrar when anonymous; username + Sair when logged in), footer

---

### Phase 6 — Frontend: Page Templates

25. **`core/templates/core/home.html`** *(create)*: hero (headline + 2 CTA buttons), "Como podemos ajudar?" with 3 feature cards, stats row (matching reference site)
26. **`accounts/templates/accounts/login.html`** *(create)*: centered card — email input + "Enviar link de acesso" button, link to /cadastro/
27. **`accounts/templates/accounts/cadastro.html`** *(create)*: centered card — nome, sobrenome, cpf, email, telefone, endereço
28. **`core/templates/core/pontos_descarte.html`** *(create)*: Bootstrap filter tabs (Todos / Recicláveis / Eletrônicos / Móveis/Entulho / Óleo), Leaflet map div, PontoDeColeta cards (nome, endereço, horário, material badges)
29. **`core/templates/core/denuncia_form.html`** *(create)*: descricão, foto upload, "Capturar localização" GPS button, hidden lat/lng inputs
30. **`core/templates/core/agendamento_form.html`** *(create)*: descricão, tipo de item, volume estimado, date picker
31. **solicitacao_list.html** *(update)*: Bootstrap card/table layout, color-coded status badges, tipo badge, dates
32. **solicitacao_detail.html** *(update)*: full info card, reschedule history as a timeline
33. **`core/templates/core/faq.html`** *(create)*: Bootstrap accordion with Q&A

---

### Phase 7 — Frontend: JavaScript

34. **GPS capture** in `denuncia_form.html`: `navigator.geolocation.getCurrentPosition()` → populate hidden lat/lng inputs; show coordinates to user
35. **Leaflet map** in `pontos_descarte.html`: init map, drop markers from JSON context, popup with nome/endereço/materiais per marker
36. **Filter logic** in `pontos_descarte.html`: clicking a material tab toggles card visibility + Leaflet marker layer visibility

---

### Relevant Files

| File | Action |
|---|---|
| requirements.txt | Add Pillow |
| settings.py | Fix SESAME_MAX_AGE, add bounding box constants |
| models.py | Add cpf, endereco |
| admin.py | Register Usuario |
| views.py | login, cadastro, logout views |
| accounts/urls.py | **CREATE** — login, cadastro, logout, sesame auth routes |
| models.py | Add horario to PontoDeColeta; image compression in Solicitacao.save() |
| views.py | home, pontos_descarte, denuncia, agendamento, faq + revamp list/detail |
| forms.py | DenunciaForm, AgendamentoForm with geographic validator |
| urls.py | Update all routes |
| `core/templates/base.html` | **CREATE** |
| `core/templates/core/home.html` | **CREATE** |
| `accounts/templates/accounts/login.html` | **CREATE** |
| `accounts/templates/accounts/cadastro.html` | **CREATE** |
| `core/templates/core/pontos_descarte.html` | **CREATE** |
| `core/templates/core/denuncia_form.html` | **CREATE** |
| `core/templates/core/agendamento_form.html` | **CREATE** |
| solicitacao_list.html | UPDATE |
| solicitacao_detail.html | UPDATE |
| `core/templates/core/faq.html` | **CREATE** |

---

### Verification

1. `python manage.py test` — existing scheduling tests pass
2. Register → check console email → click magic link → redirected to home as logged-in user
3. Visit `/pontos-descarte/` → map loads with markers, filter tabs hide/show cards + markers
4. Submit denúncia without photo → form validation error appears
5. Submit agendamento with date < 48h from now → validation error appears
6. Submit valid agendamento → confirmation email printed to console → appears in `/minhas-solicitacoes/`
7. Open on mobile-sized viewport → Bootstrap responsive layout renders correctly
