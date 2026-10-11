
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from .models import (
    SiteConfig,
    Pagina,
    CategoriaBlog,
    TagBlog,
    PostBlog,
    Projeto,
    Galeria,
    Contato,
    Conteudo,
)


# ==========================
# SITE CONFIG (singleton)
# ==========================

@admin.register(SiteConfig)
class SiteConfigAdmin(TranslationAdmin):
    list_display = ("nome_site", "atualizado_em")

    def has_add_permission(self, request):
        # impede criar mais de um registro de configuração
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================
# PÁGINAS
# ==========================

@admin.register(Pagina)
class PaginaAdmin(TranslationAdmin):
    list_display = ("titulo", "slug", "publicado", "atualizado_em")
    list_filter = ("publicado",)
    search_fields = ("titulo", "subtitulo")
    prepopulated_fields = {"slug": ("titulo",)}
    list_editable = ("publicado",)
    ordering = ("titulo",)


# ==========================
# BLOG
# ==========================

@admin.register(CategoriaBlog)
class CategoriaBlogAdmin(TranslationAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)


@admin.register(TagBlog)
class TagBlogAdmin(TranslationAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)


@admin.register(PostBlog)
class PostBlogAdmin(TranslationAdmin):
    list_display = ("titulo", "categoria", "publicado", "data_publicacao", "preview_capa")
    list_filter = ("publicado", "categoria", "tags")
    search_fields = ("titulo", "conteudo_html")
    prepopulated_fields = {"slug": ("titulo",)}
    autocomplete_fields = ("categoria",)
    filter_horizontal = ("tags",)
    list_editable = ("publicado",)
    date_hierarchy = "data_publicacao"
    ordering = ("-data_publicacao",)

    def preview_capa(self, obj):
        if obj.imagem_capa:
            return format_html(
                '<img src="{}" style="height:40px; border-radius:4px;" />',
                obj.imagem_capa.url,
            )
        return "—"
    preview_capa.short_description = "Capa"


CategoriaBlogAdmin.search_fields = ("nome",)  # necessário para autocomplete_fields funcionar


# ==========================
# PROJETOS
# ==========================

@admin.register(Projeto)
class ProjetoAdmin(TranslationAdmin):
    list_display = ("nome", "tecnologias", "atualizado_em", "preview_imagem")
    search_fields = ("nome", "tecnologias")
    prepopulated_fields = {"slug": ("nome",)}
    ordering = ("-criado_em",)

    def preview_imagem(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="height:40px; border-radius:4px;" />',
                obj.imagem.url,
            )
        return "—"
    preview_imagem.short_description = "Imagem"


# ==========================
# GALERIA
# ==========================

@admin.register(Galeria)
class GaleriaAdmin(TranslationAdmin):
    list_display = ("titulo", "preview_imagem", "criado_em")
    search_fields = ("titulo",)
    ordering = ("-criado_em",)

    def preview_imagem(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="height:40px; border-radius:4px;" />',
                obj.imagem.url,
            )
        return "—"
    preview_imagem.short_description = "Imagem"


# ==========================
# CONTATO
# ==========================

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "data")
    search_fields = ("nome", "email", "mensagem")
    readonly_fields = ("nome", "email", "mensagem", "data")
    ordering = ("-data",)

    def has_add_permission(self, request):
        # mensagens só chegam pelo formulário público
        return False


@admin.register(Conteudo)
class ConteudoAdmin(TranslationAdmin):
    list_display = ("slug", "titulo", "publicado", "atualizado_em")
    list_filter = ("publicado",)
    search_fields = ("slug", "titulo")
    prepopulated_fields = {"slug": ("titulo",)}
