from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_alter_perfilusuario_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='frete',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='forma_pagamento',
            field=models.CharField(
                choices=[
                    ('dinheiro', 'Dinheiro'),
                    ('pix', 'Pix'),
                    ('credito', 'Crédito'),
                    ('debito', 'Débito'),
                    ('gas_do_povo', 'Gás do Povo'),
                ],
                default='dinheiro',
                max_length=20,
            ),
        ),
    ]
