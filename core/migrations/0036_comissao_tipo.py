from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_compraestoque_reprovada'),
    ]

    operations = [
        migrations.AddField(
            model_name='comissao',
            name='tipo',
            field=models.CharField(
                choices=[('frete_fixo', 'Frete Fixo'), ('percentual', 'Percentual')],
                default='frete_fixo',
                max_length=20,
            ),
        ),
    ]
