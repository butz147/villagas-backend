from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_pedido_frete_pedido_gas_do_povo'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='frete_entrega',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Valor do frete por unidade deste produto na entrega.',
                max_digits=10,
            ),
        ),
    ]
