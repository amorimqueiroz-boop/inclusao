# Minha Jornada – App Gamificado (React)

App React que lê dados da planilha Google Sheets (sincronizada pelo Omnisfera PAE) e exibe a jornada gamificada para o estudante.

## Estrutura da Planilha (Omnisfera)

| Célula | Conteúdo |
|--------|----------|
| A1 | "HIPERFOCO DO ESTUDANTE:" |
| A2 | Valor do hiperfoco (ex: "Dinossauros") |
| A3 | linha vazia |
| A4 | "CÓDIGO ÚNICO (use no app gamificado):" |
| A5 | Código OMNI-XXXX-XXXX-XXXX |
| A6 | linha vazia |
| A7+ | Conteúdo da jornada (um parágrafo por linha) |

## Arquivos

- **services/sheetService.ts** – Busca o código na planilha pubhtml e extrai hiperfoco + conteúdo
- **components/Login.tsx** – Tela de login com input do código OMNI

## Configuração

1. **URL da planilha**  
   Em `sheetService.ts`, altere `GOOGLE_SHEET_HTML_URL` para a URL pubhtml da sua planilha:
   - Abra a planilha no Google Sheets
   - Arquivo → Compartilhar → Publicar na Web
   - Selecione "Publicar" e copie o link

2. **CORS**  
   Se o `fetch` falhar por CORS no navegador, use um proxy em `CORS_PROXY`, por exemplo:
   ```
   CORS_PROXY = 'https://api.allorigins.win/raw?url='
   ```
   Em produção, considere um backend que faça a leitura da planilha.

## Uso do conteúdo

O `Journey` retornado contém:

- **content**: texto completo da jornada (parágrafos unidos)
- **steps**: array com cada linha/parágrafo (passos da missão)
- **hyperfocus**: hiperfoco do estudante

Use `journey.steps` ou `journey.content` para exibir os passos da missão ao estudante.
