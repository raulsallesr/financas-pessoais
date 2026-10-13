# AGENTS.md — leia primeiro (qualquer IA)

Projeto **Lastro** (app de finanças do Raul; módulos Macro/FocusLens e Ativos B3). Vários
agentes de IA trabalham aqui, em duas máquinas, **sem memória compartilhada**. O repositório
é a única fonte de verdade. Protocolo completo: `docs/coordenacao/PROTOCOLO.md`.

## Antes de qualquer coisa

1. `python scripts/equipe.py iniciar` — mostra o que mudou, quem está mexendo em quê,
   o diário recente, a data dos dados e o estado do CI. (Python puro; roda sem instalar nada.)
   Se `python` não existir no sistema, use `python3` ou `py` nos mesmos comandos.
2. Leia `CONTEXT.md` (estado e próximo passo) e `docs/coordenacao/QUADRO.md` (o que está aberto,
   quem é o dono, o que depende do Raul).
3. Trabalhando no módulo Ativos? Leia também `docs/RETOMADA_EM_OUTRA_MAQUINA.md`,
   `docs/product/DIAGNOSTICO_E_PLANO_2026-10-09.md` e `docs/validation/LICOES_DADOS_PUBLICOS.md`.

## Regras que não se negociam

- **Reserve antes de editar:** `python scripts/equipe.py reservar <item>`. Árvore suja que não é
  sua é trabalho de outra IA: **não sobrescreva, não apague, não rode `git checkout --`**;
  leia `git diff`, a reserva e o diário, e pergunte ao Raul.
- **Suíte verde antes de empurrar:** `ruff check .` e `pytest tests/ -q --cov=.` (o comando exato do
  CI, cobertura mínima 85%; `python -m pytest` esconde erros de importação). Antes de cada push,
  `git pull --rebase --autostash`.
- **Confira o CI depois do push** (`equipe iniciar` mostra o último concluído). **CI vermelho na
  `main` é prioridade zero.** Teste local verde não basta: o CI roda em Linux, instalação limpa.
- **Commit escopado por caminho** (nunca `git add -A` às cegas) e mensagem por arquivo
  (`git commit -F arquivo`). Ignore o ruído de `dados/*.json` (o robô do GitHub e o app mexem nele).
- **Feche a sessão:** `python scripts/equipe.py fechar --resumo "..." --proximo "..."`.
  Isso grava o diário, libera a reserva e atualiza o quadro.
- **Verifique antes de confiar.** Reconfira o trabalho de outra IA (suíte, pipeline real,
  números contra a fonte da CVM/B3). Método em `docs/validation/LICOES_DADOS_PUBLICOS.md`.
- **Itens "Decisão do Raul" no quadro: pare e pergunte.**
- **Data do relógio (`date`), nunca deduzida.**

## Segurança e privacidade (o repositório é público)

Nunca escreva em arquivo versionado: segredo, token, chave de API, string de conexão, dado
da empresa onde o Raul trabalha, dado da carteira real, e-mail ou identificador pessoal.
Dados de mercado públicos (CVM, B3) são permitidos; dados brutos ficam fora do git.

## Linguagem do produto

Score, faixa estimada e margem calculada. **Nunca** "compre", "venda", "recomendo",
"preço-alvo", "barato", "caro" ou "oportunidade" em texto exibido ao usuário. O guardrail
`ativos/core/linguagem.py` testa isso. O módulo é de uso pessoal; abrir a terceiros exige
validação jurídica (CVM Res. 19 e 20/2021).

## Estilo de trabalho com o Raul

Português do Brasil, direto e curto, sem preâmbulo. Ele quer ver resultado na tela, não só
investigação. "Manda bala" significa seguir com a sugestão proposta. Em tarefa nova e aberta,
faça 2 a 4 perguntas de escopo antes de agir. Ele é iniciante em Git: automatize, não peça
comandos manuais.

## Papéis (resumo)

Claude do trabalho = integrador e revisor; Codex = implementador (segue spec, não decide
escopo); IAs de casa = qualquer papel com o mesmo regime; Raul = dono das decisões.

## Ferramentas que leem outro arquivo

`CLAUDE.md` (Claude Code) aponta para este. Se a sua ferramenta lê outro arquivo
(`GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules`...), crie lá um ponteiro de
uma linha para `AGENTS.md`.
