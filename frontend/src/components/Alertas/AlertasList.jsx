import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import api from '../../services/api';

export default function AlertasList() {
  const [alertas, setAlertas] = useState([]);
  const [filtroTipo, setFiltroTipo] = useState('Activa');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarAlertas();
  }, [filtroTipo]);

  const cargarAlertas = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/alertas/?estado=${filtroTipo}&limit=20`);
      setAlertas(response.data.datos || []);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Alertas</h1>
          <p className="text-slate-400">Monitoreo de ausentismo</p>
        </div>
      </div>

      <div className="card">
        <div className="flex gap-2">
          {['Activa', 'Resuelta'].map(estado => (
            <button
              key={estado}
              onClick={() => setFiltroTipo(estado)}
              className={`px-4 py-2 rounded ${
                filtroTipo === estado
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {estado}s
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {alertas.map(alerta => (
          <div
            key={alerta.id}
            className={`card border-l-4 ${
              alerta.tipo === 'Crítica'
                ? 'border-red-500'
                : 'border-amber-500'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle
                    className={alerta.tipo === 'Crítica' ? 'text-red-500' : 'text-amber-500'}
                    size={20}
                  />
                  <h3 className="text-lg font-bold text-white">
                    {alerta.participante.nombre} {alerta.participante.apellido}
                  </h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      alerta.tipo === 'Crítica'
                        ? 'bg-red-900/30 text-red-400'
                        : 'bg-amber-900/30 text-amber-400'
                    }`}
                  >
                    {alerta.tipo}
                  </span>
                </div>
                <p className="text-slate-400 text-sm mb-2">{alerta.descripcion}</p>
                <p className="text-xs text-slate-500">
                  Grupo: {alerta.grupo} • Creado: {new Date(alerta.fecha_creacion).toLocaleDateString()}
                </p>
              </div>
              <button className="btn-primary flex items-center gap-2 whitespace-nowrap ml-4">
                <CheckCircle size={18} />
                Resolver
              </button>
            </div>
          </div>
        ))}
      </div>

      {alertas.length === 0 && (
        <div className="card text-center py-8">
          <CheckCircle className="mx-auto text-green-500 mb-3" size={40} />
          <p className="text-slate-400">No hay alertas {filtroTipo.toLowerCase()}s</p>
        </div>
      )}
    </div>
  );
}