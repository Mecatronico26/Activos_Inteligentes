# Generated by Django 4.2.7 on 2025-03-03 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('activos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanMantenimientoPredictivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_plan', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('parametros_medicion', models.CharField(help_text='Parámetros que se medirán (temperatura, vibración, etc.)', max_length=200)),
                ('valor_umbral', models.FloatField(help_text='Valor umbral para generar alerta')),
                ('unidad_medida', models.CharField(max_length=50)),
                ('frecuencia_medicion', models.CharField(choices=[('diaria', 'Diaria'), ('semanal', 'Semanal'), ('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('trimestral', 'Trimestral'), ('semestral', 'Semestral'), ('anual', 'Anual')], max_length=20)),
                ('responsable', models.CharField(max_length=100)),
                ('fecha_inicio', models.DateField()),
                ('activo', models.BooleanField(default=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Plan de Mantenimiento Predictivo',
                'verbose_name_plural': 'Planes de Mantenimiento Predictivo',
                'ordering': ['activo', 'nombre_plan'],
            },
        ),
        migrations.CreateModel(
            name='Mantenimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('modelo', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('preventivo', 'Preventivo'), ('correctivo', 'Correctivo'), ('predictivo', 'Predictivo')], max_length=20)),
                ('fecha_programada', models.DateField()),
                ('fecha_realizada', models.DateField(blank=True, null=True)),
                ('responsable', models.CharField(max_length=100)),
                ('acciones', models.TextField()),
                ('estado', models.CharField(choices=[('programado', 'Programado'), ('en_proceso', 'En Proceso'), ('completado', 'Completado'), ('pospuesto', 'Pospuesto'), ('cancelado', 'Cancelado')], default='programado', max_length=20)),
                ('duracion_estimada', models.PositiveIntegerField(blank=True, help_text='Duración estimada en minutos', null=True)),
                ('duracion_real', models.PositiveIntegerField(blank=True, help_text='Duración real en minutos', null=True)),
                ('costo_estimado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('costo_real', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('requiere_parada', models.BooleanField(default=False)),
                ('requiere_repuestos', models.BooleanField(default=False)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('activo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mantenimientos', to='activos.activo')),
                ('fabricante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mantenimientos', to='activos.fabricante')),
            ],
            options={
                'verbose_name': 'Mantenimiento',
                'verbose_name_plural': 'Mantenimientos',
                'ordering': ['fecha_programada', 'tipo'],
            },
        ),
        migrations.CreateModel(
            name='LecturaPredictiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_medido', models.FloatField()),
                ('fecha_lectura', models.DateTimeField()),
                ('responsable', models.CharField(max_length=100)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('supera_umbral', models.BooleanField(default=False)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lecturas', to='mantenimiento.planmantenimientopredictivo')),
            ],
            options={
                'verbose_name': 'Lectura Predictiva',
                'verbose_name_plural': 'Lecturas Predictivas',
                'ordering': ['-fecha_lectura'],
            },
        ),
    ]
