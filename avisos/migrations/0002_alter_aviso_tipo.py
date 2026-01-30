# Generated manually for tipo field update
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avisos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aviso',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('aviso', 'Aviso'),
                    ('mensaje_sistema', 'Mensaje del Sistema'),
                    ('recordatorio', 'Recordatorio'),
                    ('urgente', 'Urgente'),
                ],
                default='aviso',
                max_length=20
            ),
        ),
    ]
