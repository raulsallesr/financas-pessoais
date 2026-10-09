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
3. Trabalhando no módulo **Lastro / Ativos B3**: leia também
   `docs/RETOMADA_EM_OUTRA_MAQUINA.md` (ambiente e dados),
   `docs/product/ROTEIRO_PROXIMAS_FASES.md` (o que falta e o desenho de cada corte) e
   `docs/validation/LICOES_DADOS_PUBLICOS.md` (erros reais dos dados públicos).

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
  Cenários e Entenda. Na web, `app_financas.py` é a entrada da plataforma
  **Lastro** (nome provisório, 2026-10-09). Ele usa `st.navigation` com dois
  módulos:
  - **Macro**: `focuslens/ui/pagina_home.py`;
  - **Ativos B3**: `ativos/ui/`.
  Páginas novas entram nessa lista, nunca em `pages/`.
- Módulo `ativos/`: mesmo padrão `core`/`adapters`/`ui`. Plano e princípios em
  `docs/product/PLANO_LASTRO.md`. Todo texto exibido passa por
  `ativos/core/linguagem.py`: score e faixa, nunca ordem nem preço-alvo. Dado
  bruto da CVM e da B3 fica em `%USERPROFILE%\.cache\lastro\`, nunca no git.
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

## Lastro / Ativos B3 — como trabalhar

Decisões do Raul (2026-10-09), que não se reabrem sem ele pedir: **uso pessoal** (repo
público é portfólio); **Python + Streamlit primeiro**, mobile depois; **fontes oficiais e
gratuitas** (CVM Dados Abertos, B3 COTAHIST, BACEN, Tesouro); plataforma "Lastro" com o
FocusLens como módulo Macro (nome provisório). Linguagem sempre de **score, faixa e
margem calculada**, nunca "compre/venda/barato/caro/oportunidade/preço-alvo"; o
guardrail `ativos/core/linguagem.py` testa isso em todo texto novo. Abrir para terceiros
exige validação jurídica (CVM Res. 19 e 20/2021).

**Ciclo que funcionou, repita:**

1. Escreva `docs/product/SPEC_<corte>.md` com fórmulas exatas, fontes, regras de
   "não se aplica", testes obrigatórios e fora de escopo (modelo: `SPEC_VALOR_ESTIMADO.md`).
2. Implemente (o Codex fez a parte pesada: `'' | codex exec --sandbox workspace-write
   --cd <repo> "<instrução>"`; veja `docs/RETOMADA_EM_OUTRA_MAQUINA.md`, seção 7).
3. **Revise sem confiar no resumo do implementador:** rode `ruff` e `pytest` você mesmo,
   rode o pipeline real, reconcilie 5 tickers contra o CSV da CVM com um cálculo
   independente, olhe distribuições e séries brutas de quem destoar, abra a tela.
   `docs/validation/LICOES_DADOS_PUBLICOS.md` explica o método e mostra o que isso já achou
   (DY zerado, escala de ações, dados sujos da CVM).
4. Commit escopado por caminho (`git checkout -- dados/` antes, para descartar o ruído do
   cache do Macro), mensagem via arquivo (`git commit -F`), `git push`.

**Regras do módulo:**

- Cálculo puro em `ativos/core`, I/O em `ativos/adapters`, telas em `ativos/ui`; nada de
  rede nem dado real nos testes (fixtures sintéticas); nunca versionar dado da CVM/B3,
  Parquet ou carteira real.
- Vazio é vazio: dado ausente ou inaplicável é `NaN`/"—", nunca zero; modelo inaplicável
  mostra o motivo; menos de 2 modelos ⇒ sem faixa.
- Todo valor estimado é **faixa** com premissas visíveis e editáveis.
- Dado com cara de erro (múltiplo absurdo, valor negativo onde não cabe) é bug a investigar
  na fonte, não número para exibir; marque com alerta.
- A coluna é `alertas` (e não `flags`, que colide com o pandas).

**Preferências do Raul:** conversa em português do Brasil, direta e curta, sem preâmbulo.
Quer ver resultado na **tela**, não só investigação. "Manda bala" significa seguir
autonomamente com a sugestão proposta. Valoriza ideias próprias além do pedido e conferência
de números contra a fonte. Em tarefas abertas e novas, faça 2 a 4 perguntas de escopo antes
de agir; em tarefas mecânicas, execute.

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
em `docs/product/PLANO_FOCUSLENS.md` (módulo Macro/mobile) e
`docs/product/PLANO_LASTRO.md` com `ROTEIRO_PROXIMAS_FASES.md` (módulo Ativos). Não duplicar
o estado entre documentos.
