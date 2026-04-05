from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_produto_frete_entrega'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compraestoque',
            name='status',
            field=models.CharField(
                choices=[
                    ('pendente', 'Pendente'),
                    ('aprovada', 'Aprovada'),
                    ('reprovada', 'Reprovada'),
                ],
                default='pendente',
                max_length=20,
            ),
        ),
    ]
