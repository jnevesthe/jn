from django.db import migrations
from django.db.models import F, Q


TRANSLATED_FIELDS = {
    "SiteConfig": ("nome_site", "descricao_curta"),
    "Pagina": ("titulo", "subtitulo", "conteudo_html"),
    "Conteudo": ("titulo", "conteudo_html"),
    "CategoriaBlog": ("nome",),
    "TagBlog": ("nome",),
    "PostBlog": ("titulo", "resumo", "conteudo_html"),
    "Projeto": ("nome", "resumo", "descricao_html"),
    "Galeria": ("titulo", "descricao_html"),
}


def copy_existing_content_to_portuguese(apps, schema_editor):
    database = schema_editor.connection.alias

    for model_name, field_names in TRANSLATED_FIELDS.items():
        model = apps.get_model("portifolio", model_name)
        manager = model.objects.using(database)

        for field_name in field_names:
            portuguese_field = f"{field_name}_pt"
            manager.filter(
                Q(**{f"{portuguese_field}__isnull": True})
                | Q(**{portuguese_field: ""})
            ).update(**{portuguese_field: F(field_name)})


class Migration(migrations.Migration):
    dependencies = [
        ("portifolio", "0012_categoriablog_nome_en_categoriablog_nome_es_and_more"),
    ]

    operations = [
        migrations.RunPython(
            copy_existing_content_to_portuguese,
            migrations.RunPython.noop,
        ),
    ]