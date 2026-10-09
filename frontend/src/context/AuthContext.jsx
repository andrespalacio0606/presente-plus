import { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [usuario = null;
  const [token = null;
  const [loading = true;
  const [rol = null;

  // Cargar sesión guardada al iniciar
  useEffect(() => {
    const tokenGuardado = localStorage.getItem('token');
    const usuarioGuardado = localStorage.getItem('usuario');
    const rolGuardado = localStorage.getItem('rol');

    if (tokenGuardado && usuarioGuardado) {
      setToken(tokenGuardado);
      setUsuario(JSON.parse(usuarioGuardado));
      setRol(rolGuardado);
    }
    setLoading(false);
  }, []);

  // Función LOGIN
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, usuario: userData, rol: rolData } = response.data;

      setToken(access_token);
      setUsuario(userData);
      setRol(rolData);

      localStorage.setItem('token', access_token);
      localStorage.setItem('usuario', JSON.stringify(userData));
      localStorage.setItem('rol', rolData);

      return true;
    } catch (error) {
      console.error('Error en login:', error);
      return false;
    }
  };

  // Función REGISTER
  const register = async (email, nombre, apellido, password, rol = 'Participante') => {
    try {
      await api.post('/auth/register', {
        email,
        nombre,
        apellido,
        password,
        rol
      });
      return true;
    } catch (error) {
      console.error('Error en registro:', error);
      return false;
    }
  };

  // Función LOGOUT
  const logout = () => {
    setToken(null);
    setUsuario(null);
    setRol(null);
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    localStorage.removeItem('rol');
  };

  return (
    <AuthContext.Provider value={{
      usuario,
      token,
      rol,
      loading,
      login,
      register,
      logout,
      estaAutenticado: !!token
    }}>
      {children}
    </AuthContext.Provider>
  );
}