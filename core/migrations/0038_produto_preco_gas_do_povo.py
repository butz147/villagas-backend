from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_comodato_item_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='preco_gas_do_povo',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Preço fixo do benefício Gás do Povo (diferente do preço normal de venda).',
                max_digits=10,
            ),
        ),
    ]
