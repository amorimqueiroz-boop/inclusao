/**
 * Minha Jornada - Serviço de leitura da Planilha Google Sheets
 *
 * Estrutura da planilha (Omnisfera):
 * - A1: "HIPERFOCO DO ESTUDANTE:"
 * - A2: Valor do hiperfoco (ex: "Dinossauros", "—")
 * - A3: linha vazia
 * - A4: "CÓDIGO ÚNICO (use no app gamificado):"
 * - A5: Código (OMNI-XXXX-XXXX-XXXX)
 * - A6: linha vazia
 * - A7+: Conteúdo da jornada (um parágrafo/etapa por linha)
 */

// Ajuste os tipos conforme seu projeto
export interface DailyMission {
  id: string;
  title: string;
  xp: number;
  isCompleted: boolean;
}

export interface Journey {
  id: string;
  title: string;
  description: string;
  subject: string;
  difficulty: string;
  totalSteps: number;
  currentStep: number;
  isCompleted: boolean;
  /** Texto completo da jornada (parágrafos unidos) */
  content?: string;
  /** Cada linha = um passo da missão */
  steps?: string[];
}

export interface SheetStudentData {
  id: string;
  name: string;
  hyperfocus: string;
  dailyMissions: DailyMission[];
  journeys: Journey[];
}

// ==================================================================================
// CONFIGURAÇÃO
// ==================================================================================
// URL pubhtml da planilha (substitua pelo ID correto do seu Google Sheets)
const GOOGLE_SHEET_HTML_URL =
  'https://docs.google.com/spreadsheets/d/e/2PACX-1vTatajVth7dMIdJBiBXengYK_xQcfxP-62j3tdpqxyBLvhI3BamZ6J49k9NqvUAWb0KD6xBWqx5OWSs/pubhtml';

// CORS: fetch do pubhtml pode bloquear no navegador. Use proxy se necessário.
// Ex: 'https://api.allorigins.win/raw?url='
const CORS_PROXY = ''; // deixe vazio para usar URL direta; ou ex: 'https://api.allorigins.win/raw?url='

// ==================================================================================
// MOCK DATA (Fallback para testes sem internet)
// ==================================================================================
const MOCK_DB: Record<string, SheetStudentData> = {
  'OMNI-TEST-1234': {
    id: 'OMNI-TEST-1234',
    name: 'Viajante Teste',
    hyperfocus: 'Astronomia',
    dailyMissions: [
      { id: 'dm1', title: 'Check-in Emocional', xp: 50, isCompleted: false },
      { id: 'dm2', title: 'Ler a Missão do Dia', xp: 50, isCompleted: false },
    ],
    journeys: [
      {
        id: 'j_mock',
        title: 'Jornada Galáctica',
        description: 'Uma aventura simulada para testes.',
        subject: 'Teste',
        difficulty: 'Fácil',
        totalSteps: 3,
        currentStep: 0,
        isCompleted: false,
        steps: ['Passo 1', 'Passo 2', 'Passo 3'],
      },
    ],
  },
};

/**
 * Extrai o nome do estudante do título da aba.
 * Formato: "Jornada Gamificada - [Nome] DD-MM HHhMM"
 */
const parseStudentName = (sheetTitle: string): string => {
  try {
    let name = sheetTitle.replace(/Jornada Gamificada\s?-\s?/i, '');
    name = name.replace(/\s*\d{2}-\d{2}\s*\d{2}h\d{2}.*$/, '');
    return name.trim() || 'Viajante';
  } catch {
    return 'Viajante';
  }
};

/**
 * Busca e interpreta o HTML do pubhtml.
 * Encontra o código na planilha e extrai hiperfoco + conteúdo.
 */
const fetchAndParseHTML = async (targetCode: string): Promise<SheetStudentData | null> => {
  try {
    const url = CORS_PROXY ? `${CORS_PROXY}${encodeURIComponent(GOOGLE_SHEET_HTML_URL)}` : GOOGLE_SHEET_HTML_URL;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Falha ao carregar planilha');

    const htmlText = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');

    const tdElements = doc.querySelectorAll('td');
    let targetCell: Element | null = null;

    for (const td of Array.from(tdElements)) {
      if (td.textContent?.trim() === targetCode) {
        targetCell = td;
        break;
      }
    }

    if (!targetCell) return null;

    const tbody = targetCell.closest('tbody');
    if (!tbody) return null;

    const rows = Array.from(tbody.querySelectorAll('tr'));

    // Extrai o texto da primeira coluna de cada linha (coluna A)
    const columnData: string[] = rows.map((tr) => {
      const cells = Array.from(tr.querySelectorAll('td'));
      return cells.length > 0 ? (cells[0].textContent?.trim() || '') : '';
    });

    const codeIndex = columnData.findIndex((val) => val === targetCode);
    if (codeIndex < 0) return null;

    // Hiperfoco: A2 = 3 linhas acima do código (A5)
    // codeIndex 4 = A5, codeIndex-3 = 1 = A2
    let hyperfocus = 'Explorador';
    if (codeIndex >= 3) {
      const val = columnData[codeIndex - 3];
      if (val && val !== 'HIPERFOCO DO ESTUDANTE:' && val !== '—') {
        hyperfocus = val;
      }
    }

    // Conteúdo: A7+ = 2 linhas abaixo do código (A5)
    // codeIndex+2 = 6 = A7
    const missionTextLines = columnData
      .slice(codeIndex + 2)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    // Nome da aba (nome do estudante)
    let studentName = 'Viajante';
    const sheetTable = targetCell.closest('table');
    if (sheetTable) {
      // Tenta obter o título da aba do elemento pai ou do documento
      const sheetDiv = sheetTable.closest('div[id]');
      const menuItems = doc.querySelectorAll('[id*="sheet-button"], .sheet-tab, [class*="sheet"]');
      for (const el of Array.from(menuItems)) {
        const text = el.textContent || '';
        if (text.includes('Jornada') || text.includes(targetCode)) {
          studentName = parseStudentName(text);
          break;
        }
      }
      if (studentName === 'Viajante') {
        const title = doc.querySelector('title')?.textContent;
        if (title) studentName = parseStudentName(title);
      }
    }

    // Monta a jornada com o conteúdo real
    const journeyId = `j_${targetCode}`;
    const content = missionTextLines.join('\n\n');
    const journey: Journey = {
      id: journeyId,
      title: `Aventura de ${studentName}`,
      description: content || 'Sua jornada personalizada de aprendizado.',
      subject: 'Jornada Integrada',
      difficulty: 'Médio',
      totalSteps: Math.max(missionTextLines.length, 1),
      currentStep: 0,
      isCompleted: false,
      content,
      steps: missionTextLines,
    };

    const dailyMissions = [
      { id: 'dm_checkin', title: 'Como estou me sentindo?', xp: 50, isCompleted: false },
      { id: 'dm_read', title: 'Ler o próximo passo da Jornada', xp: 30, isCompleted: false },
    ];

    return {
      id: targetCode,
      name: studentName,
      hyperfocus,
      dailyMissions,
      journeys: [journey],
    };
  } catch (error) {
    console.error('Erro ao processar planilha:', error);
    return null;
  }
};

/**
 * Busca os dados do estudante pelo código OMNI.
 */
export const fetchStudentFromSheet = async (accessCode: string): Promise<SheetStudentData | null> => {
  const code = accessCode.trim().toUpperCase();

  const liveData = await fetchAndParseHTML(code);
  if (liveData) return liveData;

  if (MOCK_DB[code]) return MOCK_DB[code];

  return null;
};
