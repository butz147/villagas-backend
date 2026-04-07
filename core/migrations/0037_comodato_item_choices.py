from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_comissao_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comodato',
            name='item',
            field=models.CharField(
                choices=[
                    ('P13', 'Botijão P13 (13kg)'),
                    ('P20', 'Botijão P20 (20kg)'),
                    ('P45', 'Botijão P45 (45kg)'),
                ],
                max_length=150,
            ),
        ),
    ]
