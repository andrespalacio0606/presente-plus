import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { AlertCircle } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const { register } = useContext(AuthContext);

  const [formData, setFormData] = useState({
    email: '',
    nombre: '',
    apellido: '',
    password: '',
    passwordConfirm: '',
    rol: 'Participante'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validaciones
    if (!formData.email || !formData.nombre || !formData.apellido || !formData.password) {
      setError('Por favor completa todos los campos');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.passwordConfirm) {
      setError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    // Intentar registro
    const success = await register(
      formData.email,
      formData.nombre,
      formData.apellido,
      formData.password,
      formData.rol
    );

    if (success) {
      // Redirigir a login
      navigate('/login');
    } else {
      setError('Error al crear la cuenta. El email podría estar registrado');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 shadow-xl">
          {/* Título */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-blue-400 mb-2">Presente+</h1>
            <p className="text-slate-400">Crear nueva cuenta</p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 p-3 bg-red-900/20 border border-red-700 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Formulario */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input-base"
                placeholder="usuario@ejemplo.com"
                disabled={loading}
              />
            </div>

            {/* Nombre y Apellido */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Nombre</label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  className="input-base"
                  placeholder="Juan"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Apellido</label>
                <input
                  type="text"
                  name="apellido"
                  value={formData.apellido}
                  onChange={handleChange}
                  className="input-base"
                  placeholder="Pérez"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Rol */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Rol</label>
              <select
                name="rol"
                value={formData.rol}
                onChange={handleChange}
                className="input-base"
                disabled={loading}
              >
                <option value="Participante">Participante</option>
                <option value="Educador">Educador</option>
                <option value="Coordinador">Coordinador</option>
              </select>
            </div>

            {/* Contraseña */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Contraseña</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input-base"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            {/* Confirmar Contraseña */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Confirmar Contraseña
              </label>
              <input
                type="password"
                name="passwordConfirm"
                value={formData.passwordConfirm}
                onChange={handleChange}
                className="input-base"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            {/* Botón */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-2 rounded-lg font-medium text-white transition ${
                loading
                  ? 'bg-slate-600 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {loading ? 'Creando cuenta...' : 'Crear cuenta'}
            </button>
          </form>

          {/* Link a login */}
          <div className="mt-6 text-center text-slate-400 text-sm">
            <p>¿Ya tienes cuenta? 
              <Link to="/login" className="text-blue-400 hover:text-blue-300 ml-1">
                Inicia sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}