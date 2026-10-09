import { useEffect, useState } from 'react';
import { Search, Plus, Eye, Edit2, Trash2, AlertCircle } from 'lucide-react';
import api from '../../services/api';

export default function ParticipantesList() {
  const [participantes, setParticipantes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    dni: '',
    domicilio: '',
    telefono: '',
    tutor_id: null
  });

  useEffect(() => {
    cargarParticipantes();
  }, [busqueda, filtroEstado]);

  const cargarParticipantes = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (busqueda) params.append('nombre', busqueda);
      if (filtroEstado) params.append('estado', filtroEstado);
      params.append('limit', '20');

      const response = await api.get(`/participantes/?${params}`);
      setParticipantes(response.data.datos || []);
    } catch (err) {
      setError('Error al cargar participantes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCrear = async (e) => {
    e.preventDefault();
    try {
      await api.post('/participantes/', formData);
      setShowModal(false);
      setFormData({
        nombre: '',
        apellido: '',
        dni: '',
        domicilio: '',
        telefono: '',
        tutor_id: null
      });
      cargarParticipantes();
    } catch (err) {
      setError('Error al crear participante');
      console.error(err);
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este participante?')) {
      try {
        // Nota: El backend no tiene DELETE para participantes, solo desactivar
        // Aquí mostramos cómo se haría
        alert('Función de eliminar será implementada próximamente');
      } catch (err) {
        setError('Error al eliminar participante');
      }
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
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Participantes</h1>
          <p className="text-slate-400">Gestión de participantes en el sistema</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Participante
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg flex items-center gap-2 text-red-400">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="card space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por nombre o DNI..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="input-base pl-10"
            />
          </div>

          {/* Filtro de estado */}
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="input-base"
          >
            <option value="">Todos los estados</option>
            <option value="Activo">Activo</option>
            <option value="Seguimiento">Seguimiento</option>
            <option value="Inactivo">Inactivo</option>
          </select>
        </div>
      </div>

      {/* Tabla */}
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Nombre</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">DNI</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Estado</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Grupos</th>
              <th className="text-right px-4 py-3 text-slate-400 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {participantes.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center py-8 text-slate-400">
                  No hay participantes para mostrar
                </td>
              </tr>
            ) : (
              participantes.map(p => (
                <tr key={p.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-white">{p.nombre} {p.apellido}</p>
                      <p className="text-xs text-slate-400">{p.dni}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{p.dni}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      p.estado === 'Activo'
                        ? 'bg-green-900/30 text-green-400'
                        : p.estado === 'Seguimiento'
                        ? 'bg-amber-900/30 text-amber-400'
                        : 'bg-red-900/30 text-red-400'
                    }`}>
                      {p.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    {p.grupos?.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {p.grupos.map(g => (
                          <span
                            key={g.id}
                            className="px-2 py-1 bg-blue-900/30 text-blue-400 text-xs rounded"
                          >
                            {g.nombre}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-500">Sin grupos</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 flex justify-end">
                    <button
                      className="p-2 hover:bg-slate-600 rounded text-blue-400"
                      title="Ver detalles"
                    >
                      <Eye size={18} />
                    </button>
                    <button
                      className="p-2 hover:bg-slate-600 rounded text-amber-400"
                      title="Editar"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleEliminar(p.id)}
                      className="p-2 hover:bg-slate-600 rounded text-red-400"
                      title="Eliminar"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de crear participante */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full border border-slate-700">
            <h2 className="text-2xl font-bold text-white mb-4">Nuevo Participante</h2>

            <form onSubmit={handleCrear} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  className="input-base"
                  required
                />
                <input
                  type="text"
                  placeholder="Apellido"
                  value={formData.apellido}
                  onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                  className="input-base"
                  required
                />
              </div>

              <input
                type="text"
                placeholder="DNI"
                value={formData.dni}
                onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
                className="input-base"
                required
              />

              <input
                type="text"
                placeholder="Domicilio"
                value={formData.domicilio}
                onChange={(e) => setFormData({ ...formData, domicilio: e.target.value })}
                className="input-base"
              />

              <input
                type="tel"
                placeholder="Teléfono"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="input-base"
              />

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-slate-600 rounded-lg text-slate-300 hover:bg-slate-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-success"
                >
                  Crear
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}