"""
Traduz APENAS os artigos do blog (PostBlog): titulo, resumo, slug e conteudo_html
de português para inglês e/ou espanhol.

No HTML só muda o texto visível. Tags, atributos, links, imagens, comentários e o
conteúdo de <pre>, <code>, <kbd>, <samp>, <script>, <style>, <textarea> ficam intactos.

Colocar em:  portifolio/management/commands/traduzir_artigos.py
(as pastas management/ e management/commands/ precisam de um __init__.py vazio)

Instalação:
    pip install deep-translator          # motor google (grátis)
    pip install anthropic                # só se quiseres o motor claude (pago)

Exemplos:
    python manage.py traduzir_artigos --dry-run --limite 1
    python manage.py traduzir_artigos --limite 1
    python manage.py traduzir_artigos
    python manage.py traduzir_artigos --idiomas en
    python manage.py traduzir_artigos --slug 10-ferramentas-ia-estudantes
    python manage.py traduzir_artigos --id 5 --forcar
    python manage.py traduzir_artigos --motor claude      # precisa ANTHROPIC_API_KEY

Pré-requisito: já ter corrido makemigrations, migrate e update_translation_fields.
"""
import html as htmllib
import json
import os
import re
import time

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.text import slugify

from portifolio.models import PostBlog

SKIP_TAGS = {"pre", "code", "kbd", "samp", "script", "style", "textarea"}
TOKEN_RE = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
TAG_RE = re.compile(r"^<\s*(/?)\s*([a-zA-Z0-9]+)")
HAS_LETTER = re.compile(r"[^\W\d_]", re.U)

NOMES = {"en": "English", "es": "neutral Latin American Spanish"}


# ---------------------------------------------------------------- motores
class MotorGoogle:
    def __init__(self, idioma):
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            raise CommandError("Instala primeiro: pip install deep-translator")
        self.t = GoogleTranslator(source="pt", target=idioma)

    def traduzir_lista(self, textos):
        saida = []
        esperas = [10, 30, 60, 120, 180]  # segundos entre tentativas
        for txt in textos:
            for tentativa in range(len(esperas) + 1):
                try:
                    saida.append(self.t.translate(txt) or txt)
                    break
                except Exception as e:
                    if tentativa == len(esperas):
                        raise
                    print(f"    (Google pediu para esperar; a aguardar {esperas[tentativa]}s...)")
                    time.sleep(esperas[tentativa])
            time.sleep(0.6)  # bem abaixo do limite de 5 pedidos/segundo
        return saida


class MotorClaude:
    def __init__(self, idioma, modelo):
        try:
            import anthropic
        except ImportError:
            raise CommandError("Instala primeiro: pip install anthropic")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise CommandError("Define a variável de ambiente ANTHROPIC_API_KEY.")
        self.client = anthropic.Anthropic()
        self.modelo = modelo
        tu = "you" if idioma == "en" else "tú"
        self.system = (
            f"You are a professional translator specialised in electronics, Arduino/ESP32, "
            f"programming and technology, with SEO experience. Translate Portuguese into "
            f"{NOMES[idioma]}. Address the reader as '{tu}'. Natural, fluent translation for "
            f"students and tech enthusiasts. Keep product names, brands, tools, acronyms, "
            f"units, numbers, URLs and library names untranslated. Do not add, remove or "
            f"summarise content. You receive a JSON array of strings (fragments of one "
            f"article, in order) and must return ONLY a JSON array of the same length with "
            f"each string translated. No markdown, no commentary."
        )

    def _chamar(self, textos):
        r = self.client.messages.create(
            model=self.modelo,
            max_tokens=8000,
            system=self.system,
            messages=[{"role": "user", "content": json.dumps(textos, ensure_ascii=False)}],
        )
        bruto = "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
        bruto = re.sub(r"^```(?:json)?|```$", "", bruto, flags=re.M).strip()
        dados = json.loads(bruto)
        if not isinstance(dados, list) or len(dados) != len(textos):
            raise ValueError("Resposta com tamanho diferente do pedido")
        return [str(x) for x in dados]

    def traduzir_lista(self, textos):
        saida = []
        for i in range(0, len(textos), 40):
            saida.extend(self._lote(textos[i:i + 40]))
        return saida

    def _lote(self, lote):
        try:
            return self._chamar(lote)
        except Exception:
            if len(lote) == 1:
                raise
            meio = len(lote) // 2
            return self._lote(lote[:meio]) + self._lote(lote[meio:])


# ---------------------------------------------------------------- HTML
def traduzir_html(codigo, motor):
    """Traduz só os nós de texto visíveis. Devolve o HTML com a mesma estrutura."""
    partes = TOKEN_RE.split(codigo)  # índices ímpares = tags/comentários
    profundidade = 0
    alvos = []  # (índice na lista, espaço antes, texto, espaço depois)

    for i, parte in enumerate(partes):
        if i % 2 == 1:
            if parte.startswith("<!--"):
                continue
            m = TAG_RE.match(parte)
            if m and m.group(2).lower() in SKIP_TAGS:
                if m.group(1) == "/":
                    profundidade = max(0, profundidade - 1)
                elif not parte.rstrip().endswith("/>"):
                    profundidade += 1
            continue
        if profundidade or not parte.strip() or not HAS_LETTER.search(parte):
            continue
        nucleo = parte.strip()
        antes = parte[: len(parte) - len(parte.lstrip())]
        depois = parte[len(parte.rstrip()):]
        alvos.append((i, antes, htmllib.unescape(nucleo), depois))

    if not alvos:
        return codigo

    traduzidos = motor.traduzir_lista([a[2] for a in alvos])
    for (i, antes, _orig, depois), novo in zip(alvos, traduzidos):
        seguro = htmllib.escape(novo.strip(), quote=False).replace("\xa0", "&nbsp;")
        partes[i] = antes + seguro + depois
    return "".join(partes)


def traduzir_texto(txt, motor):
    if not txt or not txt.strip():
        return txt
    return motor.traduzir_lista([htmllib.unescape(txt.strip())])[0].strip()


def cortar_resumo(txt, limite=160):
    if len(txt) <= limite:
        return txt
    corte = txt[: limite - 1].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return corte + "…"


def slug_unico(base, post, maximo=70):
    base = slugify(base)[:maximo].strip("-") or "artigo"
    candidato, n = base, 2
    while PostBlog.objects.filter(
        Q(slug=candidato) | Q(slug_pt=candidato) | Q(slug_en=candidato) | Q(slug_es=candidato)
    ).exclude(pk=post.pk).exists():
        sufixo = f"-{n}"
        candidato = base[: maximo - len(sufixo)].strip("-") + sufixo
        n += 1
    return candidato


# ---------------------------------------------------------------- comando
class Command(BaseCommand):
    help = "Traduz artigos do blog (titulo, resumo, slug, conteudo_html) de PT para EN/ES."

    def add_arguments(self, parser):
        parser.add_argument("--idiomas", nargs="+", default=["en", "es"], choices=["en", "es"])
        parser.add_argument("--motor", choices=["google", "claude"], default="google")
        parser.add_argument("--modelo-ia", default="claude-haiku-5-5")
        parser.add_argument("--id", type=int, help="Só este artigo (id)")
        parser.add_argument("--slug", help="Só este artigo (slug em português)")
        parser.add_argument("--limite", type=int, help="Máximo de artigos (para testar)")
        parser.add_argument("--forcar", action="store_true", help="Retraduz campos já preenchidos")
        parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria, sem gravar")

    def handle(self, *args, **o):
        qs = PostBlog.objects.all().order_by("id")
        if o["id"]:
            qs = qs.filter(pk=o["id"])
        if o["slug"]:
            qs = qs.filter(Q(slug_pt=o["slug"]) | Q(slug=o["slug"]))
        if o["limite"]:
            qs = qs[: o["limite"]]

        posts = list(qs)
        if not posts:
            raise CommandError("Nenhum artigo encontrado.")

        motores = {}
        for lang in o["idiomas"]:
            motores[lang] = (
                MotorGoogle(lang) if o["motor"] == "google" else MotorClaude(lang, o["modelo_ia"])
            )

        for post in posts:
            titulo_pt = getattr(post, "titulo_pt", None) or post.titulo
            resumo_pt = getattr(post, "resumo_pt", None) or post.resumo
            html_pt = getattr(post, "conteudo_html_pt", None) or post.conteudo_html
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n#{post.pk}  {titulo_pt}"))

            for lang in o["idiomas"]:
                motor = motores[lang]
                atual = {c: getattr(post, f"{c}_{lang}", "") or "" for c in
                         ("titulo", "resumo", "slug", "conteudo_html")}
                novo = {}

                try:
                    if (o["forcar"] or not atual["titulo"]) and titulo_pt:
                        novo["titulo"] = traduzir_texto(titulo_pt, motor)
                    if (o["forcar"] or not atual["resumo"]) and resumo_pt:
                        novo["resumo"] = cortar_resumo(traduzir_texto(resumo_pt, motor))
                    if (o["forcar"] or not atual["conteudo_html"]) and html_pt:
                        novo["conteudo_html"] = traduzir_html(html_pt, motor)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  [{lang}] erro: {e} — artigo ignorado neste idioma"))
                    continue

                if o["forcar"] or not atual["slug"]:
                    base_titulo = novo.get("titulo") or atual["titulo"]
                    if base_titulo:
                        novo["slug"] = slug_unico(base_titulo, post)

                if not novo:
                    self.stdout.write(f"  [{lang}] nada a fazer")
                    continue

                self.stdout.write(f"  [{lang}] campos: {', '.join(novo)}")
                if "titulo" in novo:
                    self.stdout.write(f"        título: {novo['titulo']}")
                if "slug" in novo:
                    self.stdout.write(f"        slug:   {novo['slug']}")

                if not o["dry_run"]:
                    # .update() não mexe em atualizado_em
                    PostBlog.objects.filter(pk=post.pk).update(
                        **{f"{c}_{lang}": v for c, v in novo.items()}
                    )

        self.stdout.write(self.style.SUCCESS(
            "\nSimulação concluída (nada gravado)." if o["dry_run"] else "\nConcluído."
        ))