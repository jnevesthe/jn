from django import template

register = template.Library()

@register.filter
def split_tags(value, sep=","):
    if not value:
        return []
    return [v.strip() for v in value.split(sep) if v.strip()]


# Adicionar a app/templatetags/portfolio_extras.py (o mesmo ficheiro de split_tags)

from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.utils.translation import override


@register.simple_tag(takes_context=True)
def hreflang_urls(context):
    """
    Devolve uma lista de (lang_code, lang_name, url_absoluto) para a página
    ATUAL, reconstruída em cada idioma configurado em settings.LANGUAGES.
    Páginas que não existem num certo idioma (NoReverseMatch) são ignoradas.
    """
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    resultado = []

    if not request or not match or not match.url_name:
        return resultado

    dominio = f"{request.scheme}://{request.get_host()}"

    for lang_code, lang_name in settings.LANGUAGES:
        try:
            with override(lang_code):
                caminho = reverse(match.url_name, kwargs=match.kwargs)
        except NoReverseMatch:
            continue
        resultado.append((lang_code, lang_name, f"{dominio}{caminho}"))

    return resultado

