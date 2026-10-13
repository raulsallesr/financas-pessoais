---
data: 2026-10-13T13:33
maquina: trabalho
agente: claude
itens: 0.2
commit: 14d53ca
suite: nao rodada
cobertura: nao disponivel
---
# Dados de mercado iguais nas duas maquinas: workflow diario publica a release dad
## O que fiz
Dados de mercado iguais nas duas maquinas: workflow diario publica a release dados-ativos e o sincronizar baixa em segundos; protocolo de coordenacao entre IAs concluido e simulado; CI do GitHub corrigido.
## Decisões
CI remoto e a fonte da verdade do gate; main com disciplina; arquivos mais CI sem Issues.
## O que falta
Item 1.2 (painel de qualidade de dados). Ponte com o hub da Fits depende do OK do Raul.
## Perguntas ao Raul
Nenhuma
## Fatos automáticos
- `.claude/settings.json`
- `.github/workflows/atualizar-ativos.yml`
- `.github/workflows/atualizar-curva.yml`
- `.github/workflows/atualizar-focus.yml`
- `AGENTS.md`
- `CLAUDE.md`
- `CONTEXT.md`
- `CONTRIBUTING.md`
- `README.md`
- `ativos/ui/pagina_busca.py`
- `ativos/ui/pagina_busca_fiis.py`
- `ativos/ui/pagina_ficha.py`
- `docs/RETOMADA_EM_OUTRA_MAQUINA.md`
- `docs/coordenacao/INDICE.md`
- `docs/coordenacao/PROTOCOLO.md`
- `docs/coordenacao/QUADRO.md`
- `docs/coordenacao/checkpoints/README.md`
- `docs/coordenacao/decisoes/2026-10-09_bazin-rf-fator-erp-g-mantidos.md`
- `docs/coordenacao/decisoes/2026-10-09_foco-confianca-primeiro.md`
- `docs/coordenacao/decisoes/2026-10-09_retorno-total-yahoo-so-para-preco.md`
- `docs/coordenacao/decisoes/2026-10-09_sem-demo-publica.md`
- `docs/coordenacao/decisoes/2026-10-09_uso-pessoal-streamlit-fontes-oficiais.md`
- `docs/coordenacao/decisoes/2026-10-13_arquivos-e-ci-sem-issues.md`
- `docs/coordenacao/decisoes/2026-10-13_ci-remoto-e-a-fonte-da-verdade-do-gate.md`
- `docs/coordenacao/decisoes/2026-10-13_main-com-disciplina.md`
- `docs/coordenacao/decisoes/_MOLDE.md`
- `docs/coordenacao/diario/2026-10-09_0900_trabalho-claude.md`
- `docs/coordenacao/diario/2026-10-09_1000_trabalho-codex.md`
- `docs/coordenacao/diario/2026-10-09_1657_trabalho-ia-nao-identificada.md`
- `docs/coordenacao/diario/2026-10-13_0826_trabalho-claude.md`
- `docs/coordenacao/diario/_MOLDE.md`
- `docs/coordenacao/ideias/2026-10-13_acao-vs-tesouro-ipca.md`
- `docs/coordenacao/ideias/2026-10-13_briefing-semanal-gerado-dos-dados.md`
- `docs/coordenacao/ideias/2026-10-13_issues-com-label-ideia-para-escrever-do-celular.md`
- `docs/coordenacao/ideias/2026-10-13_renda-passiva-no-laboratorio-do-dinheiro.md`
- `docs/coordenacao/ideias/2026-10-13_sensibilidade-setorial-ao-cenario-do-focus.md`
- `docs/coordenacao/ideias/2026-10-13_tirar-o-repo-do-onedrive-no-trabalho.md`
- `docs/coordenacao/ideias/2026-10-13_watchlist-proventos-e-fatos-relevantes.md`
- `docs/coordenacao/ideias/_MOLDE.md`
- `docs/coordenacao/reservas/.gitkeep`
- `docs/coordenacao/reservas/0.2.md`
- `docs/coordenacao/reservas/_MOLDE.md`
- `docs/product/SPEC_DADOS_RELEASE.md`
- `docs/product/SPEC_EQUIPE_CLI.md`
- `pyproject.toml`
- `scripts/equipe.py`
- `scripts/sincronizar_dados.py`
- `tests/test_busca_acoes_ui.py`
- `tests/test_busca_fiis_ui.py`
- `tests/test_coordenacao.py`
- `tests/test_equipe.py`
- `tests/test_ficha_ativo_ui.py`
- `tests/test_sincronizar_dados.py`
