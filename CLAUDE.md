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
- Todo código roda dentro do `.venv` do projeto (`python -m venv .venv` —
  precisa ser recriado em cada máquina, não é versionado) — nunca contra o
  Python global.
- Fluxo de código: Claude escreve direto. O protocolo de brief → Codex é
  específico do hub interno da Fits, não se aplica aqui.

## Ao terminar qualquer tarefa

1. Roda a suíte inteira (`pytest tests/`) antes de considerar pronto.
2. Atualiza `CONTEXT.md` (o que mudou, por quê, o que ficou pra próxima) —
   é o que permite a outra máquina continuar sem essa conversa.
3. Commit + `git push` (peça confirmação ao Raul antes do push, como em
   qualquer repositório — ele decide o momento, mesmo sendo repo pessoal).

## Onde queremos chegar

Visão completa e lista de próximos passos vivem em `CONTEXT.md` — não
duplicar aqui para não haver duas fontes de verdade.
