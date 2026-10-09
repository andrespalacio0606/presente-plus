import { useEffect, useState } from 'react';
import { Save, CheckCircle, XCircle, Clock } from 'lucide-react';
import api from '../../services/api';

export default function TomarAsistencia() {
  const [grupos, setGrupos] = useState([]);
  const [grupoSeleccionado, setGrupoSeleccionado] = useState('');
  const [participantes, setParticipantes] = useState([]);
  const [asistencias, setAsistencias] = useState({});
  const [loading, setLoading] = useState(false);

  const cargarGrupos = async () => {
    try {
      const response = await api.get('/grupos/?limit=20');
      setGrupos(response.data.datos || []);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const cargarParticipantes = async (grupoId) => {
    try {
      const response = await api.get(`/asistencias/grupo/${grupoId}/listos`);
      setParticipantes(response.data.participantes || []);
      // Inicializar asistencias
      const nuevasAsistencias = {};
      response.data.participantes?.forEach(p => {
        nuevasAsistencias[p.id] = 'Presente';
      });
      setAsistencias(nuevasAsistencias);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const handleGuardar = async () => {
    try {
      setLoading(true);
      const asistenciasArray = Object.entries(asistencias).map(([participanteId, estado]) => ({
        participante_id: parseInt(participanteId),
        estado
      }));

      await api.post('/asistencias/lote', {
        grupo_id: parseInt(grupoSeleccionado),
        fecha: new Date(),
        asistencias: asistenciasArray
      });

      alert('Asistencias guardadas exitosamente');
    } catch (err) {
      alert('Error al guardar asistencias');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarGrupos();
  }, []);

  useEffect(() => {
    if (grupoSeleccionado) {
      cargarParticipantes(grupoSeleccionado);
    }
  }, [grupoSeleccionado]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Tomar Asistencia</h1>
        <p className="text-slate-400">Registra la asistencia de los participantes</p>
      </div>

      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Selecciona un grupo
          </label>
          <select
            value={grupoSeleccionado}
            onChange={(e) => setGrupoSeleccionado(e.target.value)}
            className="input-base"
          >
            <option value="">-- Selecciona un grupo --</option>
            {grupos.map(g => (
              <option key={g.id} value={g.id}>
                {g.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {grupoSeleccionado && participantes.length > 0 && (
        <div className="card space-y-4">
          <h3 className="text-lg font-bold text-white mb-4">
            Participantes - {participantes.length} presentes
          </h3>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {participantes.map(p => (
              <div key={p.id} className="flex items-center gap-3 p-3 bg-slate-700/50 rounded">
                <span className="text-white flex-1">{p.nombre} {p.apellido}</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Presente' })}
                    className={`p-2 rounded ${
                      asistencias[p.id] === 'Presente'
                        ? 'bg-green-900/50 text-green-400'
                        : 'bg-slate-600 text-slate-400'
                    }`}
                  >
                    <CheckCircle size={18} />
                  </button>
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Ausente' })}
                    className={`p-2 rounded ${
                      asistencias[p.id] === 'Ausente'
                        ? 'bg-red-900/50 text-red-400'
                        : 'bg-slate-600 text-slate-400'
                    }`}
                  >
                    <XCircle size={18} />
                  </button>
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Tarde' })}
                    className={`p-2 rounded ${
                      asistencias[p.id] === 'Tarde'
                        ? 'bg-amber-900/50 text-amber-400'
                        : 'bg-slate-600 text-slate-400'
                    }`}
                  >
                    <Clock size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleGuardar}
            disabled={loading}
            className="btn-success w-full flex items-center justify-center gap-2"
          >
            <Save size={20} />
            {loading ? 'Guardando...' : 'Guardar Asistencia'}
          </button>
        </div>
      )}
    </div>
  );
}