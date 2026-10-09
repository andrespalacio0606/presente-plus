import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { AlertCircle } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validar campos
    if (!email || !password) {
      setError('Por favor completa todos los campos');
      setLoading(false);
      return;
    }

    // Intentar login
    const success = await login(email, password);

    if (success) {
      navigate('/dashboard');
    } else {
      setError('Email o contraseña incorrectos');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Card de Login */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 shadow-xl">
          {/* Logo/Título */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-blue-400 mb-2">Presente+</h1>
            <p className="text-slate-400">Sistema de Gestión de Participantes</p>
          </div>

          {/* Mensaje de error */}
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
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-base"
                placeholder="usuario@ejemplo.com"
                disabled={loading}
              />
            </div>

            {/* Contraseña */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-base"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            {/* Botón de envío */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-2 rounded-lg font-medium text-white transition ${
                loading
                  ? 'bg-slate-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
            </button>
          </form>

          {/* Enlaces */}
          <div className="mt-6 text-center text-slate-400 text-sm">
            <p>¿No tienes cuenta? 
              <Link to="/register" className="text-blue-400 hover:text-blue-300 ml-1">
                Regístrate aquí
              </Link>
            </p>
          </div>

          {/* Usuarios de prueba */}
          <div className="mt-6 p-3 bg-slate-700/50 rounded-lg text-xs text-slate-300">
            <p className="font-medium mb-2">👤 Usuarios de prueba:</p>
            <p>📧 coordinador@presente.com</p>
            <p>📧 educador@presente.com</p>
            <p>🔐 Contraseña: 123456</p>
          </div>
        </div>
      </div>
    </div>
  );
}
