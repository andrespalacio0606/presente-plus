import { useEffect, useState } from 'react';
import { Plus, Users, Calendar } from 'lucide-react';
import api from '../../services/api';

export default function GruposList() {
  const [grupos, setGrupos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarGrupos();
  }, []);

  const cargarGrupos = async () => {
    try {
      const response = await api.get('/grupos/?limit=20');
      setGrupos(response.data.datos || []);
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
          <h1 className="text-3xl font-bold text-white">Grupos</h1>
          <p className="text-slate-400">Gestión de talleres y grupos</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus size={20} />
          Nuevo Grupo
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {grupos.map(grupo => (
          <div key={grupo.id} className="card hover:shadow-lg transition">
            <h3 className="text-lg font-bold text-white mb-2">{grupo.nombre}</h3>
            <p className="text-slate-400 text-sm mb-3">{grupo.descripcion}</p>
            <div className="space-y-1 text-xs text-slate-400 mb-4">
              <p className="flex items-center gap-1">
                <Calendar size={16} />
                {grupo.dia_semana} - {grupo.horario}
              </p>
              <p className="flex items-center gap-1">
                <Users size={16} />
                {grupo.cantidad_participantes} participantes
              </p>
            </div>
            <div className="flex gap-2">
              <button className="flex-1 btn-primary text-sm">Editar</button>
              <button className="flex-1 btn-danger text-sm">Eliminar</button>
            </div>
          </div>
        ))}
      </div>

      {grupos.length === 0 && (
        <div className="card text-center py-8">
          <p className="text-slate-400">No hay grupos creados</p>
        </div>
      )}
    </div>
  );
}