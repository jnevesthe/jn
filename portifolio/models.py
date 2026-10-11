# app/models.py

from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator


def validar_extensao_imagem(valor):
    """Valida a extensão só em uploads novos; imagens já no Cloudinary vêm sem extensão."""
    nome_ficheiro = (valor.name or "").rsplit("/", 1)[-1]
    if "." not in nome_ficheiro:
        return
    FileExtensionValidator(["jpg", "jpeg", "png", "webp"])(valor)


class SiteConfig(models.Model):
    nome_site = models.CharField(max_length=150)
    logo = models.ImageField(
        upload_to="site/logo/",
        blank=True,
        null=True,
        validators=[validar_extensao_imagem]
    )
    foto_perfil = models.ImageField(
        upload_to="site/perfil/",
        blank=True,
        null=True,
        validators=[validar_extensao_imagem]
    )
    descricao_curta = models.TextField(blank=True)
    email_contato = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"

    def __str__(self):
        return self.nome_site


class Pagina(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    subtitulo = models.CharField(
        max_length=300,
        blank=True
    )

    conteudo_html = models.TextField(
        help_text="Aceita HTML personalizado"
    )

    imagem = models.ImageField(
        upload_to="paginas/",
        blank=True,
        null=True,
        validators=[validar_extensao_imagem]
    )

    publicado = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Página"
        verbose_name_plural = "Páginas"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Conteudo(models.Model):
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Nome interno único para localizar este bloco no template (ex: sobre_home)"
    )
    titulo = models.CharField(max_length=150, blank=True)
    conteudo_html = models.TextField(
        blank=True,
        help_text="Conteúdo em HTML simples (ex: <p>, <strong>, <a>)."
    )
    publicado = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conteúdo"
        verbose_name_plural = "Conteúdos"
        ordering = ["-atualizado_em"]

    def __str__(self):
        return self.titulo or self.slug


class CategoriaBlog(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class TagBlog(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class PostBlog(models.Model):

    titulo = models.CharField(max_length=200)

    resumo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Frase curta para SEO e listagens (máx. 160 caracteres recomendado)"
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    imagem_capa = models.ImageField(
        upload_to="blog/",
        validators=[validar_extensao_imagem]
    )

    conteudo_html = models.TextField(
        help_text="Aceita HTML personalizado"
    )

    categoria = models.ForeignKey(
        CategoriaBlog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(
        TagBlog,
        blank=True
    )

    publicado = models.BooleanField(
        default=True
    )

    data_publicacao = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-data_publicacao"]
        verbose_name = "Artigo"
        verbose_name_plural = "Artigos"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.titulo)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Projeto(models.Model):

    nome = models.CharField(
        max_length=200
    )

    resumo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Frase curta para SEO e listagens (máx. 160 caracteres recomendado)"
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    descricao_html = models.TextField(
        help_text="Aceita HTML personalizado"
    )

    imagem = models.ImageField(
        upload_to="projetos/",
        blank=True,
        null=True,
        validators=[validar_extensao_imagem]
    )

    tecnologias = models.CharField(
        max_length=300,
        help_text="Ex: Django, Python, React"
    )

    link_externo = models.URLField(
        blank=True
    )

    link_github = models.URLField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.nome)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Galeria(models.Model):

    titulo = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        blank=True,
        null=True
    )

    imagem = models.ImageField(
        upload_to="galeria/",
        validators=[validar_extensao_imagem]
    )

    descricao_html = models.TextField(
        blank=True,
        help_text="Aceita HTML personalizado"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Imagem da Galeria"
        verbose_name_plural = "Galeria"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.titulo)

        super().save(*args, **kwargs)


class Contato(models.Model):

    nome = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    mensagem = models.TextField()

    data = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.nome} - {self.email}"