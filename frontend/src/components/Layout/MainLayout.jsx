import { useContext, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import {
  Menu, X, LogOut, Users, BookOpen,
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
        className={`flex flex-col shrink-0 bg-slate-800 border-r border-slate-700 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        {/* Header del sidebar */}
        <div
          className={`flex items-center p-4 h-16 border-b border-slate-700 ${
            sidebarOpen ? 'justify-between' : 'justify-center'
          }`}
        >
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-blue-400">Presente+</h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 transition"
            aria-label={sidebarOpen ? 'Cerrar menú' : 'Abrir menú'}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Menú */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {itemsVisibles.map(item => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.href}
                to={item.href}
                title={item.label}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg transition ${
                    sidebarOpen ? '' : 'justify-center'
                  } ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 font-medium'
                      : 'text-slate-300 hover:bg-slate-700'
                  }`
                }
              >
                <Icon size={20} className="shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer del sidebar */}
        <div className="p-3 border-t border-slate-700 space-y-2">
          {sidebarOpen && (
            <div className="px-3 py-2 text-xs">
              <p className="text-slate-400">Conectado como:</p>
              <p className="text-white font-medium truncate">{usuario?.nombre}</p>
              <p className="text-blue-400">{rol}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            title="Cerrar sesión"
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-400 hover:bg-red-900/20 transition ${
              sidebarOpen ? '' : 'justify-center'
            }`}
          >
            <LogOut size={20} className="shrink-0" />
            {sidebarOpen && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* HEADER */}
        <header className="h-16 bg-slate-800 border-b border-slate-700 px-6 flex items-center justify-between">
          <p className="text-slate-400 text-sm">
            Bienvenido, <span className="text-white font-medium">{usuario?.nombre}</span>
          </p>
          <button
            className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 transition"
            aria-label="Configuración"
          >
            <Settings size={20} />
          </button>
        </header>

        {/* CONTENIDO */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
