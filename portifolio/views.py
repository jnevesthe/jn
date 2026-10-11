# app/views.py

from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
    FormView
)

from .models import (
    SiteConfig,
    Pagina,
    PostBlog,
    CategoriaBlog,
    Projeto,
    Galeria,
    Contato,
    Conteudo
)


# ==========================
# MIXIN: injeta o SiteConfig em todas as views
# ==========================

class SiteConfigMixin:
    """Garante que 'site' esteja disponível em todos os templates,
    não só na Home e no Contato."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site"] = SiteConfig.objects.first()
        return context


# ==========================
# HOME
# ==========================

from .models import SiteConfig, Projeto, PostBlog, Galeria, Conteudo


class HomeView(SiteConfigMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["projetos"] = Projeto.objects.order_by("-criado_em")[:6]

        context["posts"] = PostBlog.objects.filter(
            publicado=True
        ).select_related("categoria").prefetch_related("tags").order_by(
            "-data_publicacao"
        )[:3]

        context["galeria"] = Galeria.objects.order_by("-criado_em")[:6]

        context["conteudos"] = {
            c.slug: c for c in Conteudo.objects.filter(
                publicado=True
            ).order_by("-atualizado_em")
        }

        return context



class JosemarNevesView(SiteConfigMixin, TemplateView):
    template_name = "josemar_neves.html"



# ==========================
# PÁGINAS DINÂMICAS
# ==========================




from django.shortcuts import redirect
from django.urls import reverse


class PaginaDetailView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "pagina.html"
    context_object_name = "pagina"

    # slugs que já têm rota dedicada — redirecionam em vez de duplicar conteúdo
    SLUGS_REDIRECIONADOS = {
        "sobre": "sobre",
        "curriculo": "curriculo",
        "politica-de-privacidade": "politica_privacidade",
        "politica-de-cookies": "cookies",
        "termos-de-uso": "termos_uso",
    }

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug")
        if slug in self.SLUGS_REDIRECIONADOS:
            return redirect(reverse(self.SLUGS_REDIRECIONADOS[slug]), permanent=True)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Pagina.objects.filter(
            publicado=True
        )


# ==========================
# SOBRE
# ==========================

class SobreView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "sobre.html"
    context_object_name = "pagina"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Pagina,
            slug="sobre",
            publicado=True
        )



class CookiesView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "pagina.html"
    context_object_name = "pagina"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Pagina,
            slug="politica-de-cookies",
            publicado=True
        )



class AvisoLegalView(SiteConfigMixin, TemplateView):
    template_name = "aviso_legal.html"


# ==========================
# PROJETOS
# ==========================

class ProjetoListView(SiteConfigMixin, ListView):
    model = Projeto
    template_name = "projetos.html"
    context_object_name = "projetos"
    paginate_by = 12

    def get_queryset(self):
        return Projeto.objects.order_by("-criado_em")


class ProjetoDetailView(SiteConfigMixin, DetailView):
    model = Projeto
    template_name = "projeto_detail.html"
    context_object_name = "projeto"
    slug_field = "slug"
    slug_url_kwarg = "slug"


# ==========================
# BLOG
# ==========================

class BlogCategoriaView(SiteConfigMixin, ListView):
    model = PostBlog
    template_name = "blog_categoria.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        self.categoria = get_object_or_404(
            CategoriaBlog,
            slug=self.kwargs["slug"]
        )
        return PostBlog.objects.filter(
            publicado=True,
            categoria=self.categoria
        ).select_related("categoria").prefetch_related("tags").order_by(
            "-data_publicacao"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categoria"] = self.categoria
        return context


class BlogListView(SiteConfigMixin, ListView):
    model = PostBlog
    template_name = "blog.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return PostBlog.objects.filter(
            publicado=True
        ).select_related("categoria").prefetch_related("tags").order_by(
            "-data_publicacao"
        )


class BlogDetailView(SiteConfigMixin, DetailView):
    model = PostBlog
    template_name = "post.html"
    context_object_name = "post"

    def get_queryset(self):
        return PostBlog.objects.filter(
            publicado=True
        ).select_related("categoria").prefetch_related("tags")



class CategoriaListView(SiteConfigMixin, ListView):
    model = CategoriaBlog
    template_name = "categorias.html"
    context_object_name = "categorias"

    def get_queryset(self):
        return CategoriaBlog.objects.all().order_by("nome")


# ==========================
# GALERIA
# ==========================

class GaleriaListView(SiteConfigMixin, ListView):
    model = Galeria
    template_name = "galeria.html"
    context_object_name = "imagens"
    paginate_by = 20

    def get_queryset(self):
        return Galeria.objects.order_by("-criado_em")



class GaleriaDetailView(SiteConfigMixin, DetailView):
    model = Galeria
    template_name = "galeria_detail.html"
    context_object_name = "imagem"
    slug_field = "slug"
    slug_url_kwarg = "slug"


# ==========================
# CURRÍCULO
# ==========================

class CurriculoView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "curriculo.html"
    context_object_name = "pagina"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Pagina,
            slug="curriculo",
            publicado=True
        )


# ==========================
# POLÍTICA DE PRIVACIDADE
# ==========================

class PoliticaPrivacidadeView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "pagina.html"
    context_object_name = "pagina"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Pagina,
            slug="politica-de-privacidade",
            publicado=True
        )


# ==========================
# TERMOS DE USO
# ==========================

class TermosUsoView(SiteConfigMixin, DetailView):
    model = Pagina
    template_name = "pagina.html"
    context_object_name = "pagina"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Pagina,
            slug="termos-de-uso",
            publicado=True
        )


# ==========================
# CONTATO
# ==========================

class ContatoForm(forms.ModelForm):
    """Validação real dos dados (evita salvar nome/email/mensagem
    vazios ou em formato inválido, que o request.POST.get() cru
    permitia passar direto para o banco)."""

    class Meta:
        model = Contato
        fields = ["nome", "email", "mensagem"]
        widgets = {
            "mensagem": forms.Textarea(attrs={"rows": 5}),
        }


class ContatoView(SiteConfigMixin, FormView):
    template_name = "contato.html"
    form_class = ContatoForm
    success_url = reverse_lazy("contato")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Mensagem enviada com sucesso!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Não foi possível enviar sua mensagem. Verifique os campos e tente novamente."
        )
        return super().form_invalid(form)


# ==========================
# SEO
# ==========================

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: https://www.jnportfolio.space/sitemap.xml/\n",
        content_type="text/plain"
    )



# portifolio/views.py — função sitemap()
# Única diferença para a que já tens: usa slug_pt nos modelos com slug traduzido,
# para o sitemap não depender do idioma do navegador de quem o abre.

def sitemap(request):
    site = SiteConfig.objects.first()
    dominio = f"https://{request.get_host()}"

    def url_absoluto(imagem):
        """Cloudinary já devolve URL absoluto; storage local devolve caminho relativo."""
        url = imagem.url
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{dominio}{url}"

    urls = ["", "sobre/", "projetos/", "blog/", "blog/categorias/", "galeria/", "curriculo/",
            "politica-de-privacidade/", "politica-de-cookies/", "termos-de-uso/", "contato/",
            "aviso-legal/", "josemar-neves/"]

    SLUGS_RESERVADOS = {
        "sobre",
        "curriculo",
        "politica-de-privacidade",
        "politica-de-cookies",
        "termos-de-uso",
        "josemar-neves",
    }

    imagens_por_url = {}

    if site and site.foto_perfil:
        imagens_por_url["josemar-neves/"] = url_absoluto(site.foto_perfil)

    for pagina in Pagina.objects.filter(publicado=True).exclude(slug__in=SLUGS_RESERVADOS):
        urls.append(f"pagina/{pagina.slug}/")

    for projeto in Projeto.objects.all():
        url_projeto = f"projeto/{projeto.slug_pt}/"
        urls.append(url_projeto)
        if projeto.imagem:
            imagens_por_url[url_projeto] = url_absoluto(projeto.imagem)

    for post in PostBlog.objects.filter(publicado=True):
        url_post = f"blog/{post.slug_pt}/"
        urls.append(url_post)
        if post.imagem_capa:
            imagens_por_url[url_post] = url_absoluto(post.imagem_capa)

    for categoria in CategoriaBlog.objects.all():
        urls.append(f"blog/categoria/{categoria.slug_pt}/")

    for galeria in Galeria.objects.all():
        if galeria.slug_pt:
            url_galeria = f"galeria/{galeria.slug_pt}/"
            urls.append(url_galeria)
            if galeria.imagem:
                imagens_por_url[url_galeria] = url_absoluto(galeria.imagem)

    xml_urls = ""
    for u in urls:
        imagem_tag = ""
        if u in imagens_por_url:
            imagem_tag = f"<image:image><image:loc>{imagens_por_url[u]}</image:loc></image:image>"
        xml_urls += f"<url><loc>{dominio}/{u}</loc>{imagem_tag}</url>"

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
        f"{xml_urls}"
        "</urlset>"
    )

    return HttpResponse(xml, content_type="application/xml")


from django.http import HttpResponse

def ads_txt(request):
    conteudo = "google.com, pub-1687261973938075, DIRECT, f08c47fec0942fa0"
    return HttpResponse(conteudo, content_type="text/plain")