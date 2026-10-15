# portifolio/middleware.py  (criar este ficheiro)
#
# Deteta o idioma do navegador na PRIMEIRA visita à página inicial ("/") e redireciona
# para /en/ ou /es/. Regras de segurança para o SEO:
#   - só atua na home ("/"); links diretos (Google, partilhas) nunca são redirecionados
#   - só atua se a pessoa ainda não escolheu idioma (cookie "idioma_escolhido")
#   - ignora robôs/crawlers e pedidos sem cabeçalho Accept-Language (ex.: Googlebot)
#   - redirecionamento 302 (temporário), com "Vary: Accept-Language, Cookie"
#   - português (ou qualquer idioma não suportado) fica em "/" sem redirecionar

import re

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.translation.trans_real import parse_accept_lang_header

COOKIE_ESCOLHA = "idioma_escolhido"
SUPORTADOS = ("pt", "en", "es")
BOTS = re.compile(
    r"bot|crawl|spider|slurp|mediapartners|bing|yandex|baidu|duckduck|"
    r"facebookexternalhit|preview|lighthouse|pagespeed|headless|curl|wget",
    re.I,
)


class IdiomaAutomaticoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._deve_redirecionar(request):
            lang = self._idioma_preferido(request)
            if lang and lang != "pt":
                with translation.override(lang):
                    destino = reverse("home")
                query = request.META.get("QUERY_STRING", "")
                if query:
                    destino = f"{destino}?{query}"
                resposta = HttpResponseRedirect(destino)
                patch_vary_headers(resposta, ("Accept-Language", "Cookie"))
                return resposta
        return self.get_response(request)

    @staticmethod
    def _deve_redirecionar(request):
        if request.method != "GET" or request.path != "/":
            return False
        if request.COOKIES.get(COOKIE_ESCOLHA):
            return False
        if not request.META.get("HTTP_ACCEPT_LANGUAGE"):
            return False
        if BOTS.search(request.META.get("HTTP_USER_AGENT", "")):
            return False
        return True

    @staticmethod
    def _idioma_preferido(request):
        cabecalho = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        for lang, qualidade in parse_accept_lang_header(cabecalho):
            if qualidade <= 0:
                continue
            codigo = lang.lower().split("-")[0]
            if codigo in SUPORTADOS:
                return codigo
        return None