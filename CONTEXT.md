# CONTEXT — Finanças Pessoais

> Fonte de verdade operacional curta para retomada. Não é changelog.
> O histórico detalhado está no Git e nas seções 24–35 de `PLANO_FOCUSLENS.md`.
> O último handoff extenso, anterior a esta condensação, está no commit `54382df`.

## Estado em uma tela

- Produto: **FocusLens BR**, educacional e privado. `mobile/` é a interface
  principal; o app Streamlit permanece como referência funcional.
- Branch: `main`. Corte funcional: mobile `v0.6.4`, Android `versionCode 23`,
  iOS `buildNumber 23`.
- Entrega atual: revisão semanal opcional e laboratório do dinheiro organizados
  por intenção, com estado somente na sessão.
- Preview realmente instalado: `v0.5.2`, build `11`, EAS
  `c08e5397-427f-42c2-a163-ab5cd815cb55`. A instalação foi confirmada pelo
  Raul, mas não foi verificada por ADB nem avaliada fisicamente.
- Preview candidato: `v0.6.4`, build `23`, EAS
  `6ac1268d-5902-46b4-8108-457977bb7e1f`, commit `a2bb4b5`, `FINISHED` em
  2026-09-02. Não está instalado nem constitui evidência física.
- Sprint de publicação iniciado no commit `f2ed931`: licença MIT, commits via
  GitHub `noreply`, CI Python/mobile, Ruff, cobertura com piso de 85%, README,
  carrossel e demonstração MP4/GIF. O repositório continua privado.
- Decisão vigente do Raul: seguir a sequência canônica do roadmap. A Fase A
  fecha antes de qualquer implementação da Etapa 6/Embedded.
- Não rodar Maestro automaticamente. Os fluxos agora são não destrutivos e o
  runner recusa `clearState: true`, mas a execução continua manual e deliberada.
- Pendências físicas ativas: BI-04–BI-13, CL-11–CL-13, DB-10–DB-12 e E2E
  Android/iOS.

## Retomada segura

No repositório `01_Projetos/Financas-Pessoais`:

```powershell
git pull --ff-only
git status --short --branch
git stash list
```

Leia, nesta ordem:

1. `CLAUDE.md`;
2. este `CONTEXT.md`;
3. `PLANO_FOCUSLENS.md`;
4. `mobile/README.md`;
5. `docs/ARQUITETURA_MOBILE.md`.

Use somente o Git interno deste projeto. Não faça `git add`, commit ou push no
Git da raiz do hub.

## Contrato de produto que não deve ser reaberto

### Experiência

- Manter as quatro abas: **Hoje, Carteira, Cenários e Entenda**.
- A Home começa pelo recorte pessoal e explica a relação com a fotografia
  pública; não vira mural genérico de mercado.
- Diferenciar sempre **demonstração** de **carteira local**.
- Em demonstração, oferecer a entrada B3 antes da carteira fictícia.
- Preservar modo discreto, revelação progressiva, feedback de toque, rótulos
  acessíveis e alvos mínimos de 44 px.
- Não criar urgência, streak, gamificação, promessa ou incentivo a giro.

### Dados, privacidade e fronteiras

- Os motores Python `v1.12`–`v2.0` continuam sendo a fonte das leituras. Não os
  reescrever durante a evolução mobile.
- `mobile_snapshot.py` entrega somente fotografia pública já calculada no
  contrato `v1`; `snapshotProvider.ts` valida o JSON e usa fallback demo
  explícito quando necessário.
- A carteira local permanece separada do snapshot público, cifrada com
  AES-256-GCM, com chave pequena no cofre nativo e documento no filesystem
  privado do app.
- O importador B3, históricos, favoritos e persistências existentes permanecem
  com seus contratos atuais.
- Revisão guiada, família escolhida e entradas do laboratório vivem apenas em
  memória durante a sessão. Reiniciar o processo descarta esse estado.
- Não solicitar nem versionar planilha de carteira real, valores pessoais,
  identificadores ou capturas sensíveis. Evidência física deve ser sintética.

### Fora de escopo

- Alterar motores Python, fórmulas financeiras existentes, cofre, importador B3,
  persistências ou o snapshot público `v1`.
- Adicionar dependência, rede, telemetria, retorno previsto, recomendação,
  produto, ordem, autenticação, Open Finance ou Embedded.
- Preencher hipóteses com carteira, produto, instituição ou fonte externa.
- Chamar projeção educacional de garantia, plano financeiro ou taxa indicada.
- Iniciar Etapa 6 antes da decisão explícita e dos gates correspondentes.

## O que já está implementado

### Base móvel

- Fotografia pública com fonte/data, histórico, favoritos, `effects`, impactos e
  relação com posições já compostos.
- Carteira local privada, entrada manual e importação B3 sanitizada com prévia.
- Estados de demonstração, fallback/offline, modo discreto e navegação pelas
  quatro abas.
- Camadas de utilidade anteriores a `v0.5.3`: leitura pessoal da Home,
  comparação de fotografias, favoritos e exploração de impactos.

### Revisão guiada `v0.5.3`

- Entrada opcional “Revisar a semana” em Hoje.
- Sequência curta em Entenda: o que mudou, o que prova, onde toca a carteira,
  o que explorar em Cenários e o que não prova.
- Usa somente fotografia pública, favoritos, fonte/data, `effects`, impactos e
  posições já presentes em memória.
- Sem histórico, declara que não há comparação. Sem efeito, não inventa posição
  ou impacto.
- A ida a Cenários preserva o que já estava digitado, não preenche hipótese e
  permite voltar ao encerramento da revisão.

### Laboratório do dinheiro `v0.5.4`–`v0.6.4`

As experiências estão agrupadas por três intenções — começar do zero, enxergar
o caminho e testar situações da vida real — com uma família visível por vez:

- “Quanto vira?”: valor inicial, aporte mensal, taxa efetiva anual e prazo;
- meta mensal e custo de esperar para começar;
- inflação opcional, equivalente de hábitos e desafio taxa × aporte;
- dobra, marcos de patrimônio e régua temporal de 1 a 50 anos;
- equivalente mensal e aportes extras únicos ou anuais;
- caminho da reserva sem rendimento e com meta escolhida pela pessoa;
- comparação completa entre capital, aportes, juros, inflação e custo hipotético;
- plano flexível com aumento anual e pausa de aportes;
- à vista × parcelado, incluindo taxa implícita somente quando ela existe.
- duração de um saldo sob retiradas mensais, com reajuste anual opcional.

Convenções completas, fórmulas, limites e evidências de cada incremento estão
nas seções 24–35 de `PLANO_FOCUSLENS.md` e em
`docs/ARQUITETURA_MOBILE.md`.

## Evidência automatizada do corte `v0.6.4/23`

Executado em 2026-09-01 e ampliado em 2026-09-02:

- `npm run typecheck`: aprovado;
- `npm test`: 70 testes de domínio, 33 de componentes e 4 contratos E2E;
- `npm run export:android`: aprovado, bundle Android/Hermes com 656 módulos;
- viewports 375×812, 430×932, 768×1024 e 844×390: sem overflow horizontal e
  sem alvo interativo visível abaixo de 44 px, inclusive com movimento reduzido.
- Python: 191 testes, Ruff aprovado e cobertura de branches em 86,1%, com
  piso de 85% configurado no CI.

O `spawn EPERM` do export e o `WinError 5` do navegador já foram reproduzidos
dentro do sandbox e passaram em execução isolada/fora dele sem mudança de
código. Trate-os primeiro como ruído do Windows/OneDrive, não como motivo para
afrouxar gates.

O preview EAS `v0.6.4/23` terminou, mas não foi instalado. Não houve Maestro,
ADB nem avaliação física para `v0.5.3`–`v0.6.4`.

## Estado físico e toolchain

- Aparelho de referência: POCO X8 Pro, Android 16
  (`BP2A.250605.031.A3`).
- Evidência já aprovada: DB-01–DB-05 e DB-07–DB-09; DB-06 é automatizado;
  BI-01–BI-03; CL-02–CL-10.
- Ainda pendente: DB-10–DB-12, BI-04–BI-13, CL-11–CL-13 e E2E
  Android/iOS.
- Temurin `17.0.20.1`, Maestro `2.9.0` e ADB `37.0.1` estão disponíveis em
  toolchain portátil. A consulta de 2026-09-02 encontrou zero aparelhos.
- O comando `npm run e2e:maestro:device:windows` confere aparelho, package e
  versão sem abrir o app; os fluxos preservam o estado local.
- O APK candidato `v0.6.4/23` expira em 2026-09-16.

Se os testes físicos forem retomados, usar estado descartável ou fazer backup
fora do chat. Nunca inferir aprovação pela automação e nunca enviar evidência
com dados reais da carteira.

## Stashes preservados

Não aplicar, remover, renomear ou reordenar sem pedido explícito:

```text
stash@{0}: On main: codex-focus-cache-before-mobile-handoff-2026-08-27
stash@{1}: On main: codex-web-cockpit-before-mobile-pivot-2026-08-27
stash@{2}: On main: codex-pre-focuslens-cache-2026-08-26
```

## Gates de desenvolvimento

Para mudança em `mobile/`:

```powershell
cd mobile
npm run typecheck
npm test
npm run export:android
```

Validar também os quatro viewports já usados e os alvos de 44 px. Bundles de
export, quadros e perfis de captura são temporários e não devem permanecer
versionados; somente as mídias finais aprovadas em `docs/assets/` permanecem.

Para mudança Python, usar o `.venv` externo ao OneDrive indicado no `README.md`
e rodar a suíte completa:

```powershell
pip install -r requirements-dev.txt
ruff check .
python -m pytest tests/ --cov=.
```

Maestro é sempre manual e deliberado. O comando existir não autoriza executá-lo.

## Próxima decisão

- Instalar o preview `v0.6.4/23` já concluído no EAS
  `6ac1268d-5902-46b4-8108-457977bb7e1f` e conectar o POCO por USB para o gate
  ADB sem abrir o app.
- Executar Maestro somente por decisão manual do Raul. As jornadas já preservam
  o estado, mas não substituem TalkBack, texto ampliado ou o roteiro B3.
- Fechar E2E iOS com ambiente/aparelho compatível.
- Somente depois fechar receipt/threat model e iniciar a Etapa 6 na ordem da
  seção 14 de `PLANO_FOCUSLENS.md`.

## Estado da publicação pública

- O repositório continua privado.
- Licença MIT registrada; o histórico foi preservado e os próximos commits usam
  o endereço `noreply` oficial do GitHub.
- A exposição do e-mail antigo no histórico foi aceita como custo de preservar
  hashes e rastreabilidade; não exibir o endereço em documentação ou relatório.
- Tag, release e visibilidade pública exigem autorização explícita do Raul.
- A demo pública de 21,2 segundos existe em MP4 e GIF, usa somente fotografia
  pública, carteira fictícia e estado de sessão; nenhum código do app mudou.
- Publicação em loja também depende dos gates de segurança e da decisão sobre
  vulnerabilidades moderadas transitivas do toolchain Expo.

## Prompt curto para o próximo chat

> Abra `01_Projetos/Financas-Pessoais`, rode `git pull --ff-only`, confira
> `git status --short --branch` e `git stash list`, e leia `CLAUDE.md`,
> `CONTEXT.md`, `PLANO_FOCUSLENS.md`, `mobile/README.md` e
> `docs/ARQUITETURA_MOBILE.md`. Preserve os três stashes documentados. O corte
> funcional é mobile `v0.6.4/23`; o preview instalado continua
> `v0.5.2/11`, sem verificação ADB nem avaliação física. O preview candidato
> `v0.6.4/23` terminou no EAS
> `6ac1268d-5902-46b4-8108-457977bb7e1f`, mas ainda não foi instalado. Siga o
> roadmap canônico: feche primeiro os gates físicos e iOS,
> sem iniciar silenciosamente a Etapa 6. Preserve quatro abas, Home pessoal,
> distinção demo × local, modo discreto, B3 antes da carteira fictícia e estado
> novo somente na
> sessão. Não altere motores Python, snapshot `v1`, cofre, importador B3 ou
> persistências; não adicione dependência, rede, telemetria, recomendação ou
> produto. Não rode Maestro automaticamente. Os fluxos preservam estado e o
> runner recusa `clearState: true`. BI-04–BI-13, CL-11–CL-13, DB-10–DB-12 e
> E2E Android/iOS seguem pendentes. Ao concluir, rode os gates,
> atualize a documentação sem recriar um changelog no `CONTEXT.md`, remova
> temporários e faça commit/push somente no Git interno.
