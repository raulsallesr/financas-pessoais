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
- Decisão vigente do Raul: continuar melhorando utilidade e vontade de uso antes
  de priorizar a bateria física restante.
- Não rodar Maestro automaticamente: os fluxos atuais usam `clearState: true` e
  podem apagar a carteira local.
- Pendências pausadas: BI-04–BI-13, CL-11–CL-13, DB-10–DB-12 e E2E
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

Executado em 2026-09-01:

- `npm run typecheck`: aprovado;
- `npm test`: 70 testes de domínio, 33 de componentes e 4 contratos E2E;
- `npm run export:android`: aprovado, bundle Android/Hermes com 656 módulos;
- viewports 375×812, 430×932, 768×1024 e 844×390: sem overflow horizontal e
  sem alvo interativo visível abaixo de 44 px, inclusive com movimento reduzido.

O `spawn EPERM` do export e o `WinError 5` do navegador já foram reproduzidos
dentro do sandbox e passaram em execução isolada/fora dele sem mudança de
código. Trate-os primeiro como ruído do Windows/OneDrive, não como motivo para
afrouxar gates.

Não houve preview EAS, Maestro, ADB nem avaliação física para `v0.5.3`–`v0.6.4`.

## Estado físico e toolchain

- Aparelho de referência: POCO X8 Pro, Android 16
  (`BP2A.250605.031.A3`).
- Evidência já aprovada: DB-01–DB-05 e DB-07–DB-09; DB-06 é automatizado;
  BI-01–BI-03; CL-02–CL-10.
- Ainda pendente: DB-10–DB-12, BI-04–BI-13, CL-11–CL-13 e E2E
  Android/iOS.
- Temurin `17.0.20.1`, Maestro `2.9.0` e ADB `37.0.1` estão disponíveis em
  toolchain portátil. A última consulta ADB encontrou zero aparelhos.
- Os APKs internos anteriores expiram em 2026-09-11.

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

Validar também os quatro viewports já usados e os alvos de 44 px. Artefatos de
export e captura são temporários e não devem permanecer versionados.

Para mudança Python, usar o `.venv` externo ao OneDrive indicado no `README.md`
e rodar a suíte completa:

```powershell
python -m pytest tests/
```

Maestro é sempre manual e deliberado. O comando existir não autoriza executá-lo.

## Próxima decisão

- O usuário quer **mais melhorias de produto antes da bateria física**.
- Nenhum incremento posterior a `v0.6.4` está escolhido. Não inventar uma etapa
  como se estivesse aprovada; propor ou selecionar a próxima utilidade com base
  em clareza para iniciantes e motivo recorrente para voltar.
- Priorizar perguntas reconhecíveis, resposta em poucos segundos e profundidade
  opcional. Evitar empilhar novos painéis sem orientação.
- Quando houver nova entrega: atualizar este estado curto, registrar detalhes no
  `PLANO_FOCUSLENS.md`/arquitetura somente quando necessários, rodar gates,
  remover temporários e publicar no Git interno.

## Bloqueios de publicação pública

- O repositório continua privado.
- Escolher licença antes de abertura pública.
- Resolver ou aceitar a exposição do e-mail não mascarado no histórico.
- Tag, release e visibilidade pública exigem autorização explícita do Raul.
- Publicação em loja também depende dos gates de segurança e da decisão sobre
  vulnerabilidades moderadas transitivas do toolchain Expo.

## Prompt curto para o próximo chat

> Abra `01_Projetos/Financas-Pessoais`, rode `git pull --ff-only`, confira
> `git status --short --branch` e `git stash list`, e leia `CLAUDE.md`,
> `CONTEXT.md`, `PLANO_FOCUSLENS.md`, `mobile/README.md` e
> `docs/ARQUITETURA_MOBILE.md`. Preserve os três stashes documentados. O corte
> funcional é mobile `v0.6.4/23`; o preview instalado continua
> `v0.5.2/11`, sem verificação ADB nem avaliação física. Continue melhorias de
> produto para iniciantes antes da bateria física, sem escolher silenciosamente
> uma etapa não aprovada. Preserve quatro abas, Home pessoal, distinção demo ×
> local, modo discreto, B3 antes da carteira fictícia e estado novo somente na
> sessão. Não altere motores Python, snapshot `v1`, cofre, importador B3 ou
> persistências; não adicione dependência, rede, telemetria, recomendação ou
> produto. Não rode Maestro automaticamente. BI-04–BI-13, CL-11–CL-13,
> DB-10–DB-12 e E2E Android/iOS seguem pausados. Ao concluir, rode os gates,
> atualize a documentação sem recriar um changelog no `CONTEXT.md`, remova
> temporários e faça commit/push somente no Git interno.
