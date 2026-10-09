import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext, AuthProvider } from './context/AuthContext';

// Importar componentes
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import MainLayout from './components/Layout/MainLayout';
import ParticipantesList from './components/Participantes/ParticipantesList';
import GruposList from './components/Grupos/GruposList';
import TomarAsistencia from './components/Asistencia/TomarAsistencia';
import AlertasList from './components/Alertas/AlertasList';

// Componente de ruta protegida
function RutaProtegida({ children }) {
  const { estaAutenticado, loading } = useContext(AuthContext);

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-white mt-4">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppRoutes() {
  const { estaAutenticado } = useContext(AuthContext);

  return (
    <Routes>
      {/* Rutas de autenticación */}
      <Route 
        path="/login" 
        element={estaAutenticado ? <Navigate to="/dashboard" /> : <Login />} 
      />
      <Route 
        path="/register" 
        element={estaAutenticado ? <Navigate to="/dashboard" /> : <Register />} 
      />

      {/* Rutas protegidas */}
      <Route
        path="/dashboard"
        element={
          <RutaProtegida>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </RutaProtegida>
        }
      />

      <Route
        path="/participantes"
        element={
          <RutaProtegida>
            <MainLayout>
              <ParticipantesList />
            </MainLayout>
          </RutaProtegida>
        }
      />

      <Route
        path="/grupos"
        element={
          <RutaProtegida>
            <MainLayout>
              <GruposList />
            </MainLayout>
          </RutaProtegida>
        }
      />

      <Route
        path="/asistencia"
        element={
          <RutaProtegida>
            <MainLayout>
              <TomarAsistencia />
            </MainLayout>
          </RutaProtegida>
        }
      />

      <Route
        path="/alertas"
        element={
          <RutaProtegida>
            <MainLayout>
              <AlertasList />
            </MainLayout>
          </RutaProtegida>
        }
      />

      {/* Ruta por defecto */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
