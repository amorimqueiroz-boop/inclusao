import React, { useState, useMemo } from 'react';
import { 
  Users, BookOpen, Puzzle, Rocket, 
  NotebookPen, BarChart3, Landmark, 
  Compass, BrainCircuit, HelpCircle,
  TrendingUp, Minus, HeartPulse,
  Globe, Menu, User, LogOut,
  FolderOpen, Landmark as LandmarkIcon,
  BrainCircuit as BrainIcon,
  TrendingUp as TrendingIcon
} from 'lucide-react';

import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Hero } from './components/Hero';
import { ModuleCard } from './components/ModuleCard';
import { ResourceCard } from './components/ResourceCard';
import { ModuleData, ResourceData, MetricData } from './types';

// Mock Data Configuration
const WORKSPACE_NAME = "Escola Modelo";
const USER_NAME = "Rodrigo";

const MODULES: ModuleData[] = [
  {
    id: 'm_aluno',
    title: 'Estudantes',
    desc: 'Gestão completa de alunos, histórico e acompanhamento individualizado.',
    icon: Users,
    colorClass: 'text-indigo-600',
    bgClass: 'bg-indigo-50',
    borderClass: 'border-indigo-200',
    page: 'alunos'
  },
  {
    id: 'm_pei',
    title: 'Estratégias & PEI',
    desc: 'Plano Educacional Individual com objetivos, avaliações e acompanhamento.',
    icon: BookOpen,
    colorClass: 'text-blue-600',
    bgClass: 'bg-blue-50',
    borderClass: 'border-blue-200',
    page: 'pei'
  },
  {
    id: 'm_pae',
    title: 'Plano de Ação / PAEE',
    desc: 'Plano de Atendimento Educacional Especializado e sala de recursos.',
    icon: Puzzle,
    colorClass: 'text-purple-600',
    bgClass: 'bg-purple-50',
    borderClass: 'border-purple-200',
    page: 'paee'
  },
  {
    id: 'm_hub',
    title: 'Hub de Recursos',
    desc: 'Biblioteca de materiais, modelos e inteligência artificial para apoio.',
    icon: Rocket,
    colorClass: 'text-teal-600',
    bgClass: 'bg-teal-50',
    borderClass: 'border-teal-200',
    page: 'hub'
  },
  {
    id: 'm_diario',
    title: 'Diário de Bordo',
    desc: 'Registro diário de observações, evidências e intervenções.',
    icon: NotebookPen,
    colorClass: 'text-rose-600',
    bgClass: 'bg-rose-50',
    borderClass: 'border-rose-200',
    page: 'diario'
  },
  {
    id: 'm_dados',
    title: 'Evolução & Dados',
    desc: 'Indicadores, gráficos e relatórios de progresso dos alunos.',
    icon: BarChart3,
    colorClass: 'text-sky-600',
    bgClass: 'bg-sky-50',
    borderClass: 'border-sky-200',
    page: 'dados'
  },
];

const RESOURCES: ResourceData[] = [
  { 
    title: "Lei da Inclusão", 
    desc: "LBI e diretrizes", 
    icon: LandmarkIcon, 
    theme: "sky", 
    link: "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm" 
  },
  { 
    title: "Base Nacional", 
    desc: "Competências BNCC", 
    icon: Compass, 
    theme: "green", 
    link: "http://basenacionalcomum.mec.gov.br/" 
  },
  { 
    title: "Neurociência", 
    desc: "Artigos e estudos", 
    icon: BrainIcon, 
    theme: "rose", 
    link: "https://institutoneurosaber.com.br/" 
  },
  { 
    title: "Ajuda Omnisfera", 
    desc: "Tutoriais e suporte", 
    icon: HelpCircle, 
    theme: "orange", 
    link: "#" 
  },
];

const METRICS: MetricData[] = [
  { label: "Alunos Ativos", value: "12", change: "+2", trend: "up" },
  { label: "PEIs Ativos", value: "8", change: "+1", trend: "up" },
  { label: "Evidências Hoje", value: "3", change: "0", trend: "neutral" },
  { label: "Meta Mensal", value: "75%", change: "+5%", trend: "up" },
];

// Login Component
const LoginScreen = ({ onLogin }: { onLogin: () => void }) => (
  <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
    <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center border border-slate-100">
      <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-6 text-indigo-600">
        <Puzzle className="w-8 h-8" />
      </div>
      <h2 className="text-2xl font-bold text-slate-800 mb-2">Omnisfera</h2>
      <p className="text-slate-500 mb-8">Plano de Atendimento Educacional</p>
      <button 
        onClick={onLogin}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-indigo-200"
      >
        Entrar no Sistema
      </button>
    </div>
  </div>
);

// Home Dashboard Component
const HomeDashboard = ({ 
  userName, 
  onNavigate,
  onLogout 
}: { 
  userName: string; 
  onNavigate: (page: string) => void;
  onLogout: () => void;
}) => {
  return (
    <div className="animate-fade-in-up">
      <Hero userName={userName} />

      <div className="mb-8">
        <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <Rocket className="w-5 h-5 text-indigo-600" />
          Módulos da Plataforma
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {MODULES.map((mod) => (
            <div key={mod.id} className="flex flex-col">
              {/* Card Body */}
              <div className="flex h-32 bg-white border border-slate-200 rounded-t-2xl overflow-hidden group hover:-translate-y-1 hover:shadow-lg hover:border-slate-300 transition-all duration-300">
                {/* Color Bar */}
                <div className={`w-1.5 h-full ${
                  mod.colorClass.includes('indigo') ? 'bg-indigo-500' :
                  mod.colorClass.includes('blue') ? 'bg-blue-500' :
                  mod.colorClass.includes('purple') ? 'bg-purple-500' :
                  mod.colorClass.includes('teal') ? 'bg-teal-500' :
                  mod.colorClass.includes('rose') ? 'bg-rose-500' :
                  'bg-sky-500'
                }`}></div>
                
                {/* Icon Area */}
                <div className={`w-20 h-full flex items-center justify-center flex-shrink-0 ${mod.bgClass} border-r border-slate-100`}>
                  <mod.icon className={`w-8 h-8 ${mod.colorClass}`} />
                </div>

                {/* Content Area */}
                <div className="flex-1 p-5 flex flex-col justify-center">
                  <h3 className="font-extrabold text-slate-800 text-lg mb-1 leading-tight group-hover:text-indigo-600 transition-colors">
                    {mod.title}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed line-clamp-2">
                    {mod.desc}
                  </p>
                </div>
              </div>

              {/* Action Button */}
              <button 
                onClick={() => onNavigate(mod.page)}
                className="w-full py-3 bg-white border-x border-b border-slate-200 rounded-b-2xl text-xs font-bold text-slate-500 uppercase tracking-wider hover:bg-slate-50 hover:text-indigo-600 transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                <FolderOpen className="w-4 h-4" />
                Acessar {mod.title.split(' ')[0]}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-12">
        <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-indigo-600" />
          Recursos Externos & Referências
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {RESOURCES.map((res, idx) => (
            <div key={idx} className="h-24">
              <a 
                href={res.link} 
                target={res.link !== '#' ? "_blank" : "_self"}
                rel="noreferrer"
                className="block h-full group"
              >
                <div className="h-full flex items-center gap-4 p-5 bg-white border border-slate-200 rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <div className={`
                    w-12 h-12 rounded-xl flex items-center justify-center text-xl flex-shrink-0 border
                    ${res.theme === 'sky' ? 'bg-sky-50 text-sky-600 border-sky-100' :
                      res.theme === 'green' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' :
                      res.theme === 'rose' ? 'bg-rose-50 text-rose-600 border-rose-100' :
                      'bg-orange-50 text-orange-600 border-orange-100'}
                  `}>
                    <res.icon className="w-6 h-6" />
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors">
                      {res.title}
                    </span>
                    <span className="text-xs font-semibold text-slate-400 mt-0.5">
                      {res.desc}
                    </span>
                  </div>
                </div>
              </a>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-slate-200 pt-8 mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {METRICS.map((stat, idx) => (
            <div key={idx} className="flex flex-col items-center justify-center p-4 bg-white rounded-2xl border border-slate-100 shadow-sm">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{stat.label}</span>
              <div className="flex items-end gap-2">
                <span className="text-3xl font-black text-slate-800">{stat.value}</span>
                <div className={`flex items-center text-xs font-bold mb-1.5 ${
                  stat.trend === 'up' ? 'text-emerald-500' : 
                  stat.trend === 'down' ? 'text-red-500' : 
                  'text-slate-400'
                }`}>
                  {stat.trend === 'up' ? <TrendingIcon className="w-3 h-3 mr-0.5" /> : 
                   stat.trend === 'down' ? <TrendingIcon className="w-3 h-3 mr-0.5 rotate-180" /> : 
                   <Minus className="w-3 h-3 mr-0.5" />}
                  {stat.change}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Other Page Placeholder
const OtherPagePlaceholder = ({ pageName, onBack }: { pageName: string; onBack: () => void }) => (
  <div className="flex flex-col items-center justify-center h-[60vh] text-center">
    <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 text-slate-400">
      <Puzzle className="w-10 h-10" />
    </div>
    <h2 className="text-2xl font-bold text-slate-800 mb-2">Página em Construção</h2>
    <p className="text-slate-500 max-w-md">
      O módulo <strong>{pageName.toUpperCase()}</strong> está sendo preparado. Volte ao início para acessar os módulos disponíveis.
    </p>
    <button 
      onClick={onBack}
      className="mt-6 px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
    >
      Voltar para Home
    </button>
  </div>
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [activePage, setActivePage] = useState('home');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!isAuthenticated) {
    return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;
  }

  const handleNavigate = (page: string) => {
    setActivePage(page);
    setSidebarOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setActivePage('home');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-['Plus_Jakarta_Sans']">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-white to-slate-50 border-r border-slate-200 
        flex flex-col z-40 transition-transform duration-300
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} 
        md:translate-x-0 md:flex
      `}>
        {/* Logo Area */}
        <div className="h-20 flex items-center justify-center border-b border-slate-200">
          <div className="flex flex-col items-center">
            <Globe className="w-8 h-8 text-indigo-600 mb-1" />
            <span className="text-xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-indigo-600 to-purple-600">
              OMNISFERA
            </span>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-6 px-4">
          <div className="mb-4 flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest px-2">
            <Compass className="w-4 h-4" />
            <span>Navegação</span>
          </div>

          <div className="space-y-2">
            {MODULES.map((item) => (
              <button
                key={item.page}
                onClick={() => handleNavigate(item.page)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 group
                  ${activePage === item.page 
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md' 
                    : 'bg-white text-slate-600 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-100 hover:border-indigo-200 shadow-sm'
                  }
                `}
                style={{ 
                  borderLeftWidth: activePage === item.page ? '4px' : '4px', 
                  borderLeftColor: activePage === item.page ? 'transparent' : 
                    item.colorClass.includes('indigo') ? '#4F46E5' :
                    item.colorClass.includes('blue') ? '#3B82F6' :
                    item.colorClass.includes('purple') ? '#8B5CF6' :
                    item.colorClass.includes('teal') ? '#14B8A6' :
                    item.colorClass.includes('rose') ? '#E11D48' :
                    '#0284C7'
                }}
              >
                <item.icon className={`w-5 h-5 ${activePage === item.page ? 'text-white' : 'text-slate-400 group-hover:text-indigo-600'}`} />
                {item.title}
              </button>
            ))}
          </div>
        </div>

        {/* Footer / Logout */}
        <div className="p-4 border-t border-slate-200">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold text-slate-600 bg-slate-100 hover:bg-red-50 hover:text-red-600 rounded-xl transition-colors duration-200"
          >
            <LogOut className="w-4 h-4" />
            Sair do Sistema
          </button>
        </div>
      </aside>
      
      <div className="md:ml-64 flex flex-col min-h-screen">
        <Header 
          workspaceName={WORKSPACE_NAME} 
          userName={USER_NAME}
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        />

        <main className="flex-1 px-6 md:px-12 py-8 mt-20 max-w-7xl mx-auto w-full">
          {activePage === 'home' ? (
            <HomeDashboard 
              userName={USER_NAME}
              onNavigate={handleNavigate}
              onLogout={handleLogout}
            />
          ) : (
            <OtherPagePlaceholder 
              pageName={activePage}
              onBack={() => handleNavigate('home')}
            />
          )}

          <footer className="mt-16 py-8 border-t border-slate-200 text-center">
            <p className="text-xs text-slate-400 font-medium">
              <strong className="text-slate-600">Omnisfera v2.0</strong> • Plataforma de Inclusão Educacional • Desenvolvido por RODRIGO A. QUEIROZ
            </p>
            <p className="text-[10px] text-slate-300 mt-2 font-mono">
              {new Date().toLocaleString('pt-BR')}
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}

export default App;
