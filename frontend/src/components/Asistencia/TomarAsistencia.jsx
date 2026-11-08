import { useEffect, useState } from 'react';
import { Save, CheckCircle, XCircle, Clock } from 'lucide-react';
import api from '../../services/api';

export default function TomarAsistencia() {
  const [grupos, setGrupos] = useState([]);
  const [grupoSeleccionado, setGrupoSeleccionado] = useState('');
  const [participantes, setParticipantes] = useState([]);
  const [asistencias, setAsistencias] = useState({});
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState(null);

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
      setMensaje(null);
      const asistenciasArray = Object.entries(asistencias).map(([participanteId, estado]) => ({
        participante_id: parseInt(participanteId),
        estado
      }));

      await api.post('/asistencias/lote', {
        grupo_id: parseInt(grupoSeleccionado),
        fecha: new Date(),
        asistencias: asistenciasArray
      });

      setMensaje({ tipo: 'ok', texto: 'Asistencias guardadas exitosamente' });
    } catch (err) {
      setMensaje({ tipo: 'error', texto: 'Error al guardar asistencias' });
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
          <h3 className="text-lg font-bold text-white">
            Participantes
            <span className="text-slate-400 font-normal text-sm ml-2">
              {Object.values(asistencias).filter(e => e === 'Presente').length} presentes
              {' · '}
              {Object.values(asistencias).filter(e => e === 'Ausente').length} ausentes
              {' · '}
              {Object.values(asistencias).filter(e => e === 'Tarde').length} tarde
            </span>
          </h3>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {participantes.map(p => (
              <div key={p.id} className="flex items-center gap-3 p-3 bg-slate-700/50 rounded">
                <span className="text-white flex-1">{p.nombre} {p.apellido}</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Presente' })}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition ${
                      asistencias[p.id] === 'Presente'
                        ? 'bg-green-900/50 text-green-400'
                        : 'bg-slate-600 text-slate-400 hover:bg-slate-500'
                    }`}
                  >
                    <CheckCircle size={16} />
                    <span className="hidden sm:inline">Presente</span>
                  </button>
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Ausente' })}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition ${
                      asistencias[p.id] === 'Ausente'
                        ? 'bg-red-900/50 text-red-400'
                        : 'bg-slate-600 text-slate-400 hover:bg-slate-500'
                    }`}
                  >
                    <XCircle size={16} />
                    <span className="hidden sm:inline">Ausente</span>
                  </button>
                  <button
                    onClick={() => setAsistencias({ ...asistencias, [p.id]: 'Tarde' })}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition ${
                      asistencias[p.id] === 'Tarde'
                        ? 'bg-amber-900/50 text-amber-400'
                        : 'bg-slate-600 text-slate-400 hover:bg-slate-500'
                    }`}
                  >
                    <Clock size={16} />
                    <span className="hidden sm:inline">Tarde</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {mensaje && (
            <div
              className={`p-3 rounded-lg text-sm border ${
                mensaje.tipo === 'ok'
                  ? 'bg-green-900/20 border-green-700 text-green-400'
                  : 'bg-red-900/20 border-red-700 text-red-400'
              }`}
            >
              {mensaje.texto}
            </div>
          )}

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