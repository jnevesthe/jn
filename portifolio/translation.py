# portifolio/translation.py
# Alteração: "slug" passou a fazer parte dos campos traduzidos de PostBlog, Projeto, Galeria e CategoriaBlog.
# Pagina e TagBlog ficam com slug único (Pagina tem as rotas reservadas; Tag não tem URL própria).

from modeltranslation.translator import register, TranslationOptions
from .models import (
    SiteConfig,
    Pagina,
    CategoriaBlog,
    TagBlog,
    PostBlog,
    Projeto,
    Galeria,
    Conteudo,
)


@register(SiteConfig)
class SiteConfigTranslationOptions(TranslationOptions):
    fields = ("descricao_curta",)


@register(Pagina)
class PaginaTranslationOptions(TranslationOptions):
    fields = ("titulo", "subtitulo", "conteudo_html")


@register(CategoriaBlog)
class CategoriaBlogTranslationOptions(TranslationOptions):
    fields = ("nome", "slug")


@register(TagBlog)
class TagBlogTranslationOptions(TranslationOptions):
    fields = ("nome",)


@register(PostBlog)
class PostBlogTranslationOptions(TranslationOptions):
    fields = ("titulo", "resumo", "conteudo_html", "slug")


@register(Projeto)
class ProjetoTranslationOptions(TranslationOptions):
    fields = ("nome", "resumo", "descricao_html", "slug")


@register(Galeria)
class GaleriaTranslationOptions(TranslationOptions):
    fields = ("titulo", "descricao_html", "slug")


@register(Conteudo)
class ConteudoTranslationOptions(TranslationOptions):
    fields = ("titulo", "conteudo_html")