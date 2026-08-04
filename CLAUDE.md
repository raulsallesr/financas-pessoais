# financas-pessoais — instruções para o Claude

Projeto pessoal do Raul, **sem nenhuma relação com FitBank/Fits**. App
educacional de finanças pessoais (Streamlit), começando pelo interpretador
do Boletim Focus do BACEN, evoluindo para uma plataforma financeira pessoal
completa (carteira, calculadora de rentabilidade).

Este repositório é editado de mais de uma máquina (trabalho e casa), com a
mesma conta Claude mas **sem memória de conversa compartilhada entre elas**
— cada sessão começa do zero. O git (e este arquivo + `CONTEXT.md`) é a
única fonte de verdade entre sessões e máquinas.

## Antes de qualquer tarefa

1. `git pull` — pegue o que a outra máquina fez, incluindo o cache de dados
   (`dados/focus_cache.json` é versionado de propósito, para o histórico do
   Focus ficar igual nas duas máquinas).
2. Leia `CONTEXT.md` — estado vivo do projeto (arquitetura, decisões,
   bloqueios, próximos passos), com histórico versão a versão.

## Convenções do projeto

- Motor puro (sem I/O) separado de adaptador (I/O) separado de UI:
  `focus_data.py` / `motor_indicadores.py` (puro) vs. `focus_leitura.py`
  (adaptador da API do BACEN) vs. `app_financas.py` / `pages/` (UI).
- Guardrail de conteúdo, sem exceção: nenhuma regra em `motor_indicadores.py`
  ou texto em `focus_regras.py` pode usar linguagem imperativa de
  investimento ("invista", "compre", "venda", "recomendo") nem receber dado
  do usuário (patrimônio, carteira) — é conteúdo educacional, nunca
  recomendação personalizada. `tests/test_focus_regras.py` faz lint disso
  automaticamente; se adicionar indicador/regra nova, roda esse teste antes
  de considerar terminado.
- Todo código roda dentro de um `.venv` (precisa ser recriado em cada
  máquina, não é versionado) — nunca contra o Python global. **Desde
  2026-08-04 crie o `.venv` fora da pasta do projeto**, porque ela vive
  dentro do hub sincronizado pelo OneDrive e instalar pacotes ali dentro
  pode travar no meio (`pip` usa rename/hardlink para instalar wheels, o
  OneDrive intercepta e a instalação quebra com `AssertionError`). Ver
  "Como rodar" no `README.md` para o comando validado em
  `%USERPROFILE%\.venvs\financas-pessoais`.
- Fluxo de código: **Claude e Codex escrevem direto**, com a mesma
  autorização — sem brief, sem tier de risco, sem porta de revisão prévia.
  O protocolo de brief → Codex é específico do hub interno da Fits e não se
  aplica aqui (decisão do Raul, 2026-08-04, exceção permanente registrada em
  `AGENTS.md` do hub, seção "Exceção permanente —
  `01_Projetos/Financas-Pessoais/`"). Uma conversa direta com o Raul já é
  autorização suficiente para qualquer um dos dois editar este repositório.
  Restrições que continuam valendo para os dois: usar só o git deste
  projeto (nunca o do hub) e rodar os testes antes de considerar pronto.
  Commit e `git push` estão permanentemente autorizados depois do gate
  passar, sem nova confirmação a cada tarefa (decisão do Raul, 2026-08-04).

## Ao terminar qualquer tarefa

1. Roda a suíte inteira (`pytest tests/`) antes de considerar pronto.
2. Atualiza `CONTEXT.md` (o que mudou, por quê, o que ficou pra próxima) —
   é o que permite a outra máquina continuar sem essa conversa.
3. Commit + `git push` no remote próprio do projeto; a autorização é
   permanente e não precisa ser solicitada novamente.

## Onde queremos chegar

Visão completa e lista de próximos passos vivem em `CONTEXT.md` — não
duplicar aqui para não haver duas fontes de verdade.
