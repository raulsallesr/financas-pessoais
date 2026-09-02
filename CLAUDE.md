# financas-pessoais — instruções para o Claude

Projeto pessoal do Raul, **sem nenhuma relação com FitBank/Fits**. Produto
educacional de inteligência financeira, começado em Streamlit e redirecionado
explicitamente pelo Raul em 2026-08-27 para um app móvel Android/iOS. Os motores
Python continuam sendo a fonte das leituras; `mobile/` é a interface principal
em React Native/Expo/TypeScript.

Este repositório é editado de mais de uma máquina (trabalho e casa), com a
mesma conta Claude mas **sem memória de conversa compartilhada entre elas**
— cada sessão começa do zero. O git (e este arquivo + `CONTEXT.md`) é a
única fonte de verdade entre sessões e máquinas.

## Antes de qualquer tarefa

1. `git pull` — pegue o que a outra máquina fez, incluindo o cache de dados
   (`dados/focus_cache.json` é versionado de propósito, para o histórico do
   Focus ficar igual nas duas máquinas).
2. Leia `CONTEXT.md` — estado operacional curto do projeto (decisões,
   bloqueios e próximos passos). O histórico detalhado fica no Git e no plano.

## Convenções do projeto

- Motor puro (sem I/O) separado de adaptador (I/O) separado de UI:
  `focuslens/core/` (puro) vs. `focuslens/adapters/` (I/O) vs.
  `focuslens/ui/` (Streamlit).
- Importações Excel usam `openpyxl`;
  `focuslens/adapters/b3_importacao.py` é o adaptador da
  posição B3. Nunca versione planilha real nem seus valores/identificadores.
  Testes de importação devem gerar o XLSX sintético em memória durante o
  próprio teste.
- A experiência de produto agora está em `mobile/`, com Hoje, Carteira,
  Cenários e Entenda. A referência Streamlit permanece em página única:
  `app_financas.py` chama `focuslens/ui/pagina_home.py`, sem novos entrypoints
  em `pages/`.
  Não remover nem reescrever os motores `v1.12`–`v2.0` durante a migração.
- Guardrail de conteúdo, sem exceção: nenhuma regra em
  `focuslens/core/motor_indicadores.py` ou texto em
  `focuslens/core/focus_regras.py` pode usar linguagem imperativa de
  investimento ("invista", "compre", "venda", "recomendo") nem receber dado
  do usuário (patrimônio, carteira) — é conteúdo educacional, nunca
  recomendação personalizada. `tests/test_focus_regras.py` faz lint disso
  automaticamente; se adicionar indicador/regra nova, roda esse teste antes
  de considerar terminado. O cruzamento com valores pessoais pertence
  exclusivamente a `focuslens/core/carteira_modelo.py`, fora do motor
  educacional.
- Todo código roda dentro de um `.venv` (precisa ser recriado em cada
  máquina, não é versionado) — nunca contra o Python global. **Desde
  2026-08-04 crie o `.venv` fora da pasta do projeto**, porque ela vive
  dentro do hub sincronizado pelo OneDrive e instalar pacotes ali dentro
  pode travar no meio (`pip` usa rename/hardlink para instalar wheels, o
  OneDrive intercepta e a instalação quebra com `AssertionError`). Ver
  "Como rodar" no `README.md` para o comando validado em
  `%USERPROFILE%\.venvs\financas-pessoais`.
- O app móvel usa Node.js LTS. Em checkouts dentro de OneDrive, mantenha
  `node_modules` fora da árvore sincronizada ou trabalhe em um clone de caminho
  curto; os milhares de arquivos do Expo e caminhos nativos longos tornam uma
  instalação direta instável. Nunca versione `node_modules`, `.expo/`, bundles
  ou dados pessoais.
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

1. Roda a suíte inteira (`pytest tests/`) quando tocar Python. Ao tocar
   `mobile/`, roda `npm run typecheck`, `npm run test:domain` e
   `npm run export:android`. Mudança transversal passa pelos dois gates.
2. Atualiza `CONTEXT.md` (o que mudou, por quê, o que ficou pra próxima) —
   é o que permite a outra máquina continuar sem essa conversa.
3. Commit + `git push` no remote próprio do projeto; a autorização é
   permanente e não precisa ser solicitada novamente.

## Onde queremos chegar

Visão completa e próximos passos vivem em `CONTEXT.md`; o plano detalhado está
em `docs/product/PLANO_FOCUSLENS.md`. Não duplicar o estado entre documentos.
