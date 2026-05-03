import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Upload from './pages/Upload';
import Careers from './pages/Careers';
import Gaps from './pages/Gaps';
import Quiz from './pages/Quiz';
import Interview from './pages/Interview';
import Report from './pages/Report';
import Dashboard from './pages/Dashboard';

// Protect pages that need login
const Guard = ({ children }: { children: ReactNode }) => {
  return localStorage.getItem('token') ? <>{children}</> : <Navigate to="/login" replace />;
};

export default function App() {
  const isAuthed = Boolean(localStorage.getItem('token'));

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={isAuthed ? '/dashboard' : '/login'} replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Guard><Dashboard /></Guard>} />
        <Route path="/upload" element={<Guard><Upload /></Guard>} />
        <Route path="/careers" element={<Guard><Careers /></Guard>} />
        <Route path="/gaps" element={<Guard><Gaps /></Guard>} />
        <Route path="/quiz" element={<Guard><Quiz /></Guard>} />
        <Route path="/interview" element={<Guard><Interview /></Guard>} />
        <Route path="/report" element={<Guard><Report /></Guard>} />
        <Route path="*" element={<Navigate to={isAuthed ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  );
}