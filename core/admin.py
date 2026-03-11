from django.contrib import admin

from .models import Material, PontoDeColeta, Solicitacao, Reschedule


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(PontoDeColeta)
class PontoDeColetaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco')
    filter_horizontal = ('materiais_aceitos',)


@admin.register(Reschedule)
class RescheduleAdmin(admin.ModelAdmin):
    list_display = ('solicitacao', 'old_date', 'new_date', 'changed_at')
    list_filter = ('changed_at',)


@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_solicitacao', 'status', 'requested_date', 'scheduled_date')
    list_filter = ('tipo_solicitacao', 'status')
    readonly_fields = ('data_criacao',)
