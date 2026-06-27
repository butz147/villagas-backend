from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_produto_preco_gas_do_povo'),
    ]

    operations = [
        migrations.AddField(
            model_name='compraestoque',
            name='cheios_entram',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='compraestoque',
            name='cheios_saem',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='compraestoque',
            name='vazios_entram',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='compraestoque',
            name='vazios_saem',
            field=models.IntegerField(default=0),
        ),
    ]
