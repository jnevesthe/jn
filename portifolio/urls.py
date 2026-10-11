from django.urls import path, include
from . import views


# ===== Rotas SEM prefixo de idioma =====
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),  # necessário para o formulário de troca de idioma

    path("sitemap.xml/", views.sitemap, name="sitemap"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("ads.txt/", views.ads_txt, name="ads_txt"),
]


# ===== Rotas COM prefixo de idioma (lista simples; o i18n_patterns é aplicado no urls.py raiz) =====
i18n_urlpatterns = [

    # Home
    path("", views.HomeView.as_view(), name="home"),

    # Perfil pessoal (SEO no nome)
    path("josemar-neves/", views.JosemarNevesView.as_view(), name="josemar_neves"),

    # Páginas dinâmicas
    path("pagina/<slug:slug>/", views.PaginaDetailView.as_view(), name="pagina"),

    # Sobre
    path("sobre/", views.SobreView.as_view(), name="sobre"),

    path("politica-de-cookies/", views.CookiesView.as_view(), name="cookies"),

    # Projetos
    path("projetos/", views.ProjetoListView.as_view(), name="projetos"),
    path("projeto/<slug:slug>/", views.ProjetoDetailView.as_view(), name="projeto_detail"),

    # Blog
    path("blog/", views.BlogListView.as_view(), name="blog"),
    path("blog/categorias/", views.CategoriaListView.as_view(), name="categorias"),
    path("blog/categoria/<slug:slug>/", views.BlogCategoriaView.as_view(), name="blog_categoria"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="post_detail"),

    # Galeria
    path("galeria/", views.GaleriaListView.as_view(), name="galeria"),
    path("galeria/<slug:slug>/", views.GaleriaDetailView.as_view(), name="galeria_detail"),

    # Contato
    path("contato/", views.ContatoView.as_view(), name="contato"),

    # Currículo
    path("curriculo/", views.CurriculoView.as_view(), name="curriculo"),

    # Política de privacidade
    path("politica-de-privacidade/", views.PoliticaPrivacidadeView.as_view(), name="politica_privacidade"),

    # Termos de uso
    path("termos-de-uso/", views.TermosUsoView.as_view(), name="termos_uso"),

    # Aviso Legal
    path("aviso-legal/", views.AvisoLegalView.as_view(), name="aviso_legal"),
]
