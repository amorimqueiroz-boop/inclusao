import React, { useState } from 'react';
import type { SheetStudentData } from '../services/sheetService';
import { fetchStudentFromSheet } from '../services/sheetService';

interface LoginProps {
  onLogin: (data: SheetStudentData) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [accessCode, setAccessCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const formatCode = (val: string) => {
    return val.toUpperCase().replace(/[^A-Z0-9-]/g, '');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessCode.trim()) return;

    setLoading(true);
    setError('');

    try {
      const data = await fetchStudentFromSheet(accessCode.trim());
      if (data) {
        onLogin(data);
      } else {
        setError('Código não encontrado. Verifique se digitou corretamente (Ex: OMNI-XXXX-XXXX-XXXX).');
      }
    } catch {
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-indigo-500 p-6 text-white relative overflow-hidden">
      <div className="absolute top-0 left-0 w-64 h-64 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 -translate-x-1/2 -translate-y-1/2" />
      <div className="absolute bottom-0 right-0 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 translate-x-1/2 translate-y-1/2" />

      <div className="max-w-md w-full bg-white/10 backdrop-blur-md p-8 rounded-3xl border border-white/20 shadow-2xl relative z-10 animate-fade-in-up">
        <h1 className="text-4xl font-extrabold mb-2 text-center text-white drop-shadow-md">
          Minha Jornada 🚀
        </h1>
        <p className="text-indigo-100 text-center mb-8 font-medium">
          Digite o código da sua ficha OMNI.
        </p>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-indigo-100 text-sm font-bold mb-2 ml-2">
              Seu Código OMNI
            </label>
            <input
              type="text"
              value={accessCode}
              onChange={(e) => setAccessCode(formatCode(e.target.value))}
              className="w-full px-5 py-4 rounded-2xl bg-white/90 text-indigo-900 font-bold placeholder-indigo-300 focus:outline-none focus:ring-4 focus:ring-indigo-300 transition-all shadow-inner uppercase tracking-widest text-center text-xl"
              placeholder="OMNI-XXXX-XXXX-XXXX"
              maxLength={20}
              autoFocus
            />
          </div>

          {error && (
            <div className="bg-red-400/20 border border-red-400/50 rounded-xl p-3 text-red-100 text-sm font-bold text-center animate-shake">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!accessCode.trim() || loading}
            className={`w-full py-4 rounded-2xl font-black text-lg uppercase tracking-wider transition-all transform ${
              accessCode.trim().length >= 10 && !loading
                ? 'bg-yellow-400 text-yellow-900 shadow-xl shadow-yellow-900/20 hover:scale-105 hover:bg-yellow-300'
                : 'bg-white/10 text-white/40 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⌛</span> Buscando Missões...
              </span>
            ) : (
              'Iniciar Jornada!'
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-indigo-200 text-xs opacity-70">
          Precisa de ajuda? Peça ao seu professor.
        </div>
      </div>
    </div>
  );
};

export default Login;
