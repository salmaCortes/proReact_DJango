# Generated by Django 4.2.14 on 2024-07-26 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firmas_views', '0004_rename_documento_padre_id_documentoversion_documento_padre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='documento',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
