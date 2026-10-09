import { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import {
  Menu, X, LogOut, BarChart3, Users, BookOpen, 
  Clock, AlertCircle, Settings, Home
} from 'lucide-react';

export default function MainLayout({ children }) {
  const { usuario, rol, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Menú dinámico según el rol
  const menuItems = [
    { icon: Home, label: 'Dashboard', href: '/dashboard' },
    { icon: Users, label: 'Participantes', href: '/participantes', roles: ['Coordinador', 'Educador'] },
    { icon: BookOpen, label: 'Grupos', href: '/grupos', roles: ['Coordinador', 'Educador'] },
    { icon: Clock, label: 'Asistencia', href: '/asistencia', roles: ['Coordinador', 'Educador'] },
    { icon: AlertCircle, label: 'Alertas', href: '/alertas', roles: ['Coordinador', 'Educador'] },
  ];

  // Filtrar items según el rol
  const itemsVisibles = menuItems.filter(item => !item.roles || item.roles.includes(rol));

  return (
    <div className="flex h-screen bg-slate-900">
      {/* SIDEBAR */}
      <aside
        className={`bg-slate-800 border-r border-slate-700 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        {/* Header del sidebar */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-blue-400">Presente+</h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-slate-700 rounded-lg text-slate-400"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Menú */}
        <nav className="p-4 space-y-2">
          {itemsVisibles.map(item => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                to={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-300 hover:bg-slate-700 transition"
              >
                <Icon size={20} className="flex-shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer del sidebar */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700 space-y-2">
          {sidebarOpen && (
            <div className="px-3 py-2 text-xs">
              <p className="text-slate-400">Conectado como:</p>
              <p className="text-white font-medium truncate">{usuario?.nombre}</p>
              <p className="text-blue-400 text-xs">{rol}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-red-400 hover:bg-red-900/20 transition"
          >
            <LogOut size={20} />
            {sidebarOpen && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER */}
        <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Dashboard</h2>
            <p className="text-slate-400 text-sm">Bienvenido, {usuario?.nombre}</p>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-slate-700 rounded-lg text-slate-400">
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* CONTENIDO */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}