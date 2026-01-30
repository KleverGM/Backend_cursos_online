from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import EventoUsuario
from ..serializers import EventoUsuarioSerializer
from ..permissions import IsAdminUser
from datetime import datetime, timedelta
from django.db.models import Count


class EventoUsuarioViewSet(viewsets.ViewSet):
    """ViewSet para gestionar eventos de analytics"""
    
    def get_permissions(self):
        """
        - Crear: Usuarios autenticados
        - Leer/Estadísticas: Solo admin
        """
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def create(self, request):
        """Registrar un nuevo evento"""
        serializer = EventoUsuarioSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            evento = serializer.save()
            return Response(
                EventoUsuarioSerializer(evento, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        """Listar eventos (solo admin)"""
        usuario_id = request.query_params.get('usuario_id')
        tipo_evento = request.query_params.get('tipo_evento')
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        # Construir query
        query = {}
        if usuario_id:
            query['usuario_id'] = int(usuario_id)
        if tipo_evento:
            query['tipo_evento'] = tipo_evento
        
        # Filtros de fecha
        if fecha_desde or fecha_hasta:
            query['fecha_hora__gte'] = datetime.fromisoformat(fecha_desde) if fecha_desde else datetime.min
            query['fecha_hora__lte'] = datetime.fromisoformat(fecha_hasta) if fecha_hasta else datetime.utcnow()
        
        eventos = EventoUsuario.objects(**query).order_by('-fecha_hora')[:100]
        
        serializer = EventoUsuarioSerializer(list(eventos), many=True, context={'request': request})
        return Response({
            'count': eventos.count(),
            'results': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de un evento específico (solo admin)"""
        try:
            evento = EventoUsuario.objects.get(pk=pk)
            serializer = EventoUsuarioSerializer(evento, context={'request': request})
            return Response(serializer.data)
        except EventoUsuario.DoesNotExist:
            return Response(
                {'error': 'Evento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas_usuario(self, request):
        """Estadísticas de un usuario específico"""
        usuario_id = request.query_params.get('usuario_id')
        
        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eventos = list(EventoUsuario.objects(usuario_id=int(usuario_id)))
        
        # Calcular estadísticas
        total_eventos = len(eventos)
        eventos_por_tipo = {}
        for evento in eventos:
            eventos_por_tipo[evento.tipo_evento] = eventos_por_tipo.get(evento.tipo_evento, 0) + 1
        
        # Cursos más visitados
        cursos_visitados = {}
        for evento in eventos:
            if evento.curso_id:
                cursos_visitados[evento.curso_id] = cursos_visitados.get(evento.curso_id, 0) + 1
        
        cursos_top = sorted(cursos_visitados.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return Response({
            'usuario_id': int(usuario_id),
            'total_eventos': total_eventos,
            'eventos_por_tipo': eventos_por_tipo,
            'cursos_mas_visitados': [
                {'curso_id': curso_id, 'visitas': visitas}
                for curso_id, visitas in cursos_top
            ]
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de actividad recientes"""
        from cursos.models import Curso
        
        # Fechas
        ahora = datetime.utcnow()
        inicio_hoy = datetime(ahora.year, ahora.month, ahora.day)
        inicio_semana = ahora - timedelta(days=7)
        inicio_mes = ahora - timedelta(days=30)
        
        # Eventos hoy
        eventos_hoy = EventoUsuario.objects(fecha_hora__gte=inicio_hoy).count()
        
        # Eventos semana
        eventos_semana = EventoUsuario.objects(fecha_hora__gte=inicio_semana).count()
        
        # Eventos mes
        eventos_mes = EventoUsuario.objects(fecha_hora__gte=inicio_mes).count()
        
        # Usuarios activos (únicos en el mes)
        eventos_mes_list = list(EventoUsuario.objects(fecha_hora__gte=inicio_mes))
        usuarios_activos = len(set(e.usuario_id for e in eventos_mes_list))
        
        # Eventos por tipo (mes)
        eventos_por_tipo = {}
        for evento in eventos_mes_list:
            eventos_por_tipo[evento.tipo_evento] = eventos_por_tipo.get(evento.tipo_evento, 0) + 1
        
        # Cursos más visitados (mes)
        cursos_visitas = {}
        for evento in eventos_mes_list:
            if evento.curso_id and evento.tipo_evento == 'curso_view':
                cursos_visitas[evento.curso_id] = cursos_visitas.get(evento.curso_id, 0) + 1
        
        cursos_top = sorted(cursos_visitas.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Obtener títulos de cursos
        cursos_mas_visitados = []
        for curso_id, visitas in cursos_top:
            try:
                curso = Curso.objects.get(id=curso_id)
                cursos_mas_visitados.append({
                    'curso_id': curso_id,
                    'titulo': curso.titulo,
                    'visitas': visitas
                })
            except Curso.DoesNotExist:
                # Si el curso fue eliminado, incluirlo de todas formas
                cursos_mas_visitados.append({
                    'curso_id': curso_id,
                    'titulo': f'Curso #{curso_id} (eliminado)',
                    'visitas': visitas
                })
        
        return Response({
            'total_eventos': eventos_mes,
            'eventos_hoy': eventos_hoy,
            'eventos_semana': eventos_semana,
            'eventos_mes': eventos_mes,
            'usuarios_activos': usuarios_activos,
            'eventos_por_tipo': eventos_por_tipo,
            'cursos_mas_visitados': cursos_mas_visitados
        })

    
    @action(detail=False, methods=['get'])
    def estadisticas_globales(self, request):
        """Estadísticas globales de la plataforma"""
        dias = int(request.query_params.get('dias', 7))
        fecha_desde = datetime.utcnow() - timedelta(days=dias)
        
        eventos = list(EventoUsuario.objects(fecha_hora__gte=fecha_desde))
        
        # Usuarios activos
        usuarios_activos = len(set(e.usuario_id for e in eventos))
        
        # Eventos por tipo
        eventos_por_tipo = {}
        for evento in eventos:
            eventos_por_tipo[evento.tipo_evento] = eventos_por_tipo.get(evento.tipo_evento, 0) + 1
        
        # Eventos por día
        eventos_por_dia = {}
        for evento in eventos:
            fecha = evento.fecha_hora.date().isoformat()
            eventos_por_dia[fecha] = eventos_por_dia.get(fecha, 0) + 1
        
        return Response({
            'periodo_dias': dias,
            'total_eventos': len(eventos),
            'usuarios_activos': usuarios_activos,
            'eventos_por_tipo': eventos_por_tipo,
            'eventos_por_dia': eventos_por_dia
        })
    
    @action(detail=False, methods=['get'])
    def cursos_populares(self, request):
        """Cursos más populares por vistas"""
        dias = int(request.query_params.get('dias', 30))
        fecha_desde = datetime.utcnow() - timedelta(days=dias)
        
        eventos = EventoUsuario.objects(
            tipo_evento='curso_view',
            fecha_hora__gte=fecha_desde
        )
        
        cursos_stats = {}
        for evento in eventos:
            if evento.curso_id:
                if evento.curso_id not in cursos_stats:
                    cursos_stats[evento.curso_id] = {
                        'curso_id': evento.curso_id,
                        'vistas': 0,
                        'usuarios_unicos': set()
                    }
                cursos_stats[evento.curso_id]['vistas'] += 1
                cursos_stats[evento.curso_id]['usuarios_unicos'].add(evento.usuario_id)
        
        # Convertir a lista y ordenar
        cursos_list = [
            {
                'curso_id': stats['curso_id'],
                'vistas': stats['vistas'],
                'usuarios_unicos': len(stats['usuarios_unicos'])
            }
            for stats in cursos_stats.values()
        ]
        
        cursos_list.sort(key=lambda x: x['vistas'], reverse=True)
        
        return Response({
            'periodo_dias': dias,
            'cursos': cursos_list[:10]
        })
