import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, Clock, AlertCircle, TrendingUp, Calendar, Plus, ClipboardCheck } from 'lucide-react';
import api from '../../services/api';

const COLORES = {
  blue: { texto: 'text-blue-400', fondo: 'bg-blue-500/15' },
  green: { texto: 'text-green-400', fondo: 'bg-green-500/15' },
  amber: { texto: 'text-amber-400', fondo: 'bg-amber-500/15' },
  red: { texto: 'text-red-400', fondo: 'bg-red-500/15' },
};

function Tarjeta({ icon: Icon, titulo, valor, subtitulo, color }) {
  const c = COLORES[color];
  return (
    <div className="card hover:shadow-lg transition">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-slate-400 text-sm mb-1">{titulo}</p>
          <p className={`text-3xl font-bold ${c.texto}`}>{valor}</p>
          <p className="text-slate-500 text-xs mt-1">{subtitulo}</p>
        </div>
        <div className={`p-3 rounded-lg shrink-0 ${c.fondo}`}>
          <Icon className={c.texto} size={24} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [metricas, setMetricas] = useState({
    participantesActivos: 0,
    gruposActivos: 0,
    asistenciaHoy: 0,
    alertasActivas: 0
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarMetricas();
  }, []);

  const cargarMetricas = async () => {
    try {
      // Cargar participantes
      const respParticipantes = await api.get('/participantes/?limit=1');
      // Cargar grupos
      const respGrupos = await api.get('/grupos/?limit=1');
      // Cargar alertas activas
      const respAlertas = await api.get('/alertas/activas');

      setMetricas({
        participantesActivos: respParticipantes.data.total || 0,
        gruposActivos: respGrupos.data.total || 0,
        asistenciaHoy: Math.floor(Math.random() * 100), // Placeholder
        alertasActivas: respAlertas.data.total || 0
      });
    } catch (error) {
      console.error('Error cargando métricas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-slate-400 mt-4">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Título */}
      <div>
        <h1 className="text-3xl font-bold text-white">Panel de Control</h1>
        <p className="text-slate-400">Resumen general del sistema</p>
      </div>

      {/* Grid de tarjetas de métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Tarjeta
          icon={Users}
          titulo="Participantes Activos"
          valor={metricas.participantesActivos}
          subtitulo="En el sistema"
          color="blue"
        />
        <Tarjeta
          icon={BookOpen}
          titulo="Grupos Activos"
          valor={metricas.gruposActivos}
          subtitulo="Talleres en ejecución"
          color="green"
        />
        <Tarjeta
          icon={Clock}
          titulo="Asistencia Hoy"
          valor={`${metricas.asistenciaHoy}%`}
          subtitulo="Promedio de asistencia"
          color="amber"
        />
        <Tarjeta
          icon={AlertCircle}
          titulo="Alertas Activas"
          valor={metricas.alertasActivas}
          subtitulo="Requieren atención"
          color="red"
        />
      </div>

      {/* Sección de acciones rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Acciones rápidas */}
        <div className="card">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={20} />
            Acciones Rápidas
          </h3>
          <div className="space-y-2">
            <Link to="/participantes" className="btn-primary flex items-center gap-2 w-full">
              <Plus size={18} /> Registrar Participante
            </Link>
            <Link to="/grupos" className="btn-primary flex items-center gap-2 w-full">
              <Plus size={18} /> Crear Grupo
            </Link>
            <Link to="/asistencia" className="btn-primary flex items-center gap-2 w-full">
              <ClipboardCheck size={18} /> Tomar Asistencia
            </Link>
          </div>
        </div>

        {/* Alertas recientes */}
        <div className="card">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <AlertCircle size={20} />
            Alertas Recientes
          </h3>
          {metricas.alertasActivas > 0 ? (
            <div className="space-y-2 text-sm">
              <div className="p-2 bg-red-900/20 border border-red-700 rounded text-red-400">
                3 inasistencias consecutivas - Carlos García
              </div>
              <div className="p-2 bg-amber-900/20 border border-amber-700 rounded text-amber-400">
                2 inasistencias consecutivas - María López
              </div>
            </div>
          ) : (
            <p className="text-slate-400 text-sm">No hay alertas activas</p>
          )}
        </div>
      </div>

      {/* Información adicional */}
      <div className="card bg-slate-700/50">
        <div className="flex items-start gap-3">
          <Calendar className="text-blue-400 shrink-0 mt-1" />
          <div>
            <h4 className="font-bold text-white">Próximas jornadas</h4>
            <p className="text-slate-400 text-sm mt-1">
              Las clases programadas para esta semana están siendo monitoreadas.
              Revisa el módulo de Asistencia para más detalles.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}