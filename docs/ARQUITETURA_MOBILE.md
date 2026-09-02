# Arquitetura — FocusLens Mobile

## Decisão de produto

Desde 2026-08-27, o destino principal do FocusLens é um app móvel Android/iOS.
O Streamlit permanece como referência funcional dos motores `v1.12`–`v2.0` e
como bancada de validação, não como a interface final do produto.

O app foi iniciado em React Native + Expo + TypeScript porque a mesma base
entrega Android e iOS, permite testar rapidamente em aparelho real e mantém
uma separação clara entre interface, contrato e inteligência financeira.

## Fronteiras

```text
FONTES PÚBLICAS
BACEN · Tesouro · SGS
        │
        ▼
MOTORES PYTHON EXISTENTES
Focus · Curva · Convergência · Radar · Carteira
        │
        ▼  adaptador local sem rede
CONTRATO MÓVEL
veredito · sinais · efeitos por classe · data · fonte · limites
        │
        ▼
APP REACT NATIVE
Hoje · Carteira · Cenários · Entenda
```

Os motores Python continuam como fonte das leituras públicas. O app não
reimplementar mediana, relevância do Focus, comparação D-5/D-21 ou estados de
convergência. `mobile_snapshot.py` entrega somente contratos já calculados em
`mobile/src/data/liveSnapshot.json`.

## Estado do corte `mobile v0.6.4`

O diretório `mobile/` contém a experiência completa de navegação e consome o
snapshot público `v1`. A fotografia sintética em `src/data/demoSnapshot.ts`
permanece como fallback explícito e nunca é confundida com dado vivo.

No Android/iOS, a pessoa já pode substituir conscientemente as posições
fictícias por uma carteira privada `v1`, criada e editada no próprio aparelho.
Essa carteira não altera o snapshot público nem entra no Git, EAS, telemetria
ou rede. No renderer web, o editor permanece bloqueado e somente a demo é
exibida, porque não há cofre nativo equivalente nessa bancada.

O domínio TypeScript faz apenas operações locais necessárias à experiência:

- soma e peso da carteira ativa (demo ou privada);
- agrupamento e peso por classe, sem classificação financeira nova;
- cobertura dos sinais calculada apenas pela presença dos `effects` recebidos;
- filtro de posições por classe;
- junção entre o efeito já declarado no snapshot e as posições relacionadas;
- sensibilidade educacional discreta a choques de juros;
- simulação aritmética de um aporte escolhido pela pessoa sobre pesos por classe;
- projeções educacionais determinísticas com taxa e prazo digitados pela
  pessoa, sem ler carteira, snapshot ou fonte externa.

A sensibilidade móvel é uma demonstração própria e está rotulada como tal. Ela
não substitui `curva_cenarios.py`, não calcula preço ou retorno e não entra nos
motores aprovados da `v2.0`.

### Camada de utilidade `v0.4.1`

O refinamento reorganiza somente a apresentação e cálculos locais derivados do
documento já carregado. Hoje começa pela concentração da carteira e pela
cobertura efetiva dos sinais; Carteira mostra distribuição por classe antes das
posições e expande listas longas sob demanda. Sinais e filtros não dependem mais
de gesto horizontal como interação principal.

`allocationByClass` apenas soma valores por `AssetClass`. `signalCoverage`
considera coberta uma posição somente quando algum sinal recebido contém um
efeito não vazio para a classe. Um mapa `effects` vazio produz cobertura zero e
uma mensagem de limite; nunca dispara inferência, remapeamento ou efeito criado
no TypeScript. Motores Python, snapshot público `v1`, cofre privado e importador
B3 permanecem idênticos.

### Modo discreto e resumo de Cenários `v0.4.2`

O estado `valuesHidden` vive em `App.tsx` e é repassado às três telas que podem
mostrar montantes. Ele dura somente durante a sessão: não entra no cofre, no
filesystem, no snapshot público ou em nova preferência persistida. O mesmo
controle acessível usa papel de switch e alvo mínimo de 48 px em Carteira e
Cenários.

`summarizeScenarioAllocation` recebe somente os `PortfolioImpact` já produzidos
por `buildRateScenario`. A função soma percentuais por `SignalTone`, conta
posições e calcula a parcela não coberta por diferença contra a carteira total.
Ela não escolhe o efeito, não cria sensibilidade para classe ausente e não
altera a matriz educacional. Cenários mostra essa síntese antes das posições e
limita a lista inicial a quatro itens.

### Hierarquia pessoal da Home `v0.4.3`

A Home renderiza o recorte pessoal antes do contexto público. `largestPosition`
seleciona somente a posição de maior `amount` já presente no contrato ativo e
calcula seu percentual com `allocationPercent`; a interface exibe nome e peso,
nunca o montante. Maior classe e cobertura continuam vindo de
`allocationByClass` e `signalCoverage`.

A ação principal é uma decisão de navegação, não financeira: demonstração ou
cofre indisponível levam à Carteira; carteira local leva a Cenários. O mercado
permanece inalterado e aparece depois sob “Mercado em uma frase”. Nenhum campo,
efeito, estado persistido ou chamada de rede foi adicionado.

### Entrada pessoal direta `v0.4.4`

`PortfolioScreen` muda somente a ordem e a ênfase da apresentação conforme o
modo já existente. Em demonstração, `B3ImportPanel` vem antes do patrimônio
fictício e sua escolha de XLSX é a ação principal; o editor manual permanece
como alternativa. Em carteira local, adicionar posição continua sendo a ação
principal e a importação permanece abaixo das posições como substituição.

O painel recebe o mesmo `onSavePositions` por um adaptador de feedback da tela.
Prévia, confirmação, parsing, sanitização e gravação continuam no fluxo já
implementado. Nenhum estado novo é persistido e nenhuma informação da planilha
é movida para o snapshot público ou para logs.

### Acompanhamento explicável `v0.5.0`

A Etapa 5C começa com duas persistências independentes da carteira privada:

- `focuslens-public-history-v1.json` guarda no diretório privado do app até oito
  documentos públicos que passaram por `validateLiveSnapshot`;
- `focuslens.favorite-signals.v1` guarda no SecureStore somente uma lista
  limitada e sem duplicidade de IDs públicos.

O histórico usa arquivo temporário e substituição do destino. Cada fotografia é
deduplicada por `generatedAt`; qualquer chave pública proibida pelo contrato,
inclusive `position`, `positions` ou `amount`, impede a leitura ou gravação. A
comparação observa somente veredito, ID, valor, mudança, headline e tom literais.
Ela não converte percentuais, estima direção ou recalcula motor.

`buildExplainableAlert` combina o sinal selecionado com os `effects` já
recebidos e com `impactsForSignal`. A saída separa mudança, prova, alcance e
limite. Se o mapa de efeitos vier vazio, a resposta declara ausência de relação
classificada. Favoritar muda somente a ordem da lista; não altera prioridade,
tom ou conteúdo do sinal.

### Simulador local de aportes `v0.5.1`

`simulateClassContribution` recebe o snapshot ativo, um valor positivo e uma
`AssetClass` já prevista no contrato. A função agrupa os montantes existentes,
soma o aporte somente à classe escolhida e devolve total, percentual e variação
em pontos percentuais antes/depois. A fotografia recebida não é mutada.

O estado do formulário e da hipótese permanece em `ContributionSimulatorPanel`.
Ele não usa storage, filesystem, rede ou identificador de posição; alterar valor
ou classe descarta o resultado anterior. A UI exige seleção explícita, aceita
entrada monetária brasileira e deixa retorno, risco, imposto, produto e ordem
fora do resultado. Motores Python e snapshot público `v1` permanecem inalterados.

### Arquitetura de testes `v0.5.2`

A pirâmide móvel possui três executores independentes:

- `node:test` recebe somente JavaScript compilado do domínio e não monta React;
- `jest-expo` + React Native Testing Library montam componentes com os mocks
  oficiais do Expo e verificam estado, semântica e interação;
- Maestro opera o binário final pela camada de acessibilidade, sem biblioteca
  E2E dentro do aplicativo.

`src/testing/testIds.json` é o contrato único entre componentes, testes e
fluxos. `tests/e2e/maestroFlows.test.cjs` rejeita app ID divergente, seletor não
registrado ou texto com marcador de dado pessoal. A execução estática não é
evidência física: os dois fluxos em `e2e/maestro/flows` ainda precisam rodar em
Android e iOS.

No Windows, `scripts/run-maestro-windows.ps1` resolve o toolchain portátil apenas
para o processo atual, impede execuções Maestro concorrentes e falha antes da
jornada se o ADB não tiver um aparelho autorizado selecionado ou se package,
`versionName` e `versionCode` divergirem de `app.json`. A checagem de sintaxe foi
executada no Maestro `2.9.0`; nenhum dispositivo estava conectado, portanto isso
não constitui evidência E2E física.

O Raul confirmou depois a instalação do preview `v0.5.2/11`, mas o aparelho
continuou ausente do ADB; package, versão e jornadas não foram verificados. Os
YAMLs foram tornados não destrutivos em 2026-09-02: reiniciam somente o processo
com `clearState: false`, preservando carteira, cofre, histórico e favoritos. O
runner recusa `clearState: true` e oferece um gate ADB que confere aparelho,
package e versão sem abrir o app nem executar Maestro.

As dependências de teste permanecem em `devDependencies`; Metro confirmou 650
módulos no bundle Android. Nenhum motor, storage ou contrato público/privado foi
alterado.

### Revisão guiada da semana `v0.5.3`

`App.tsx` mantém um `WeeklyReviewSession` efêmero com somente ID público do
sinal, passo atual e a informação de retorno de Cenários. Esse objeto não entra
em SecureStore, filesystem, histórico público, carteira privada ou qualquer
provider. Reiniciar o processo descarta a revisão inteira.

`WeeklyReviewPanel` é uma orquestração de apresentação sobre funções e objetos
existentes:

- `comparePublicSnapshots` fornece a mudança literal, sem converter o valor;
- `buildExplainableAlert` fornece prova, alcance e limite;
- `impactsForSignal` fornece os efeitos e posições já compostos em memória;
- os IDs persistidos de favoritos servem apenas como contexto visual;
- fonte e data vêm do próprio `MarketSignal` selecionado.

A sequência abre um passo por vez: mudança, prova, relação com a carteira,
exploração em Cenários e limite. Sem duas fotografias, declara ausência de
comparação; sem `effects`, não cria impacto. A navegação para Cenários apenas
troca a aba e marca o retorno: não escreve valor, classe ou choque. O painel de
contexto em Cenários devolve a pessoa à etapa final da mesma sessão.

Entenda preserva a metodologia geral sob revelação progressiva. Hoje mantém o
recorte pessoal e a leitura pública antes da entrada da revisão. As quatro abas,
safe areas, modo discreto e composições de carteira permanecem inalterados.
TypeScript, 42 testes de domínio, 10 de componentes, 4 contratos E2E e o bundle
Android/Hermes com 651 módulos passaram; os quatro viewports canônicos ficaram
sem overflow ou alvo visível abaixo de 44 px.

### Laboratório do dinheiro `v0.5.4`–`v0.6.4`

`moneyLab.ts` é um domínio puro e independente dos motores Python. Ele recebe
somente números digitados no laboratório e usa a taxa efetiva anual informada
para derivar a taxa mensal equivalente:

```text
i_mensal = (1 + i_anual)^(1/12) - 1
valor futuro = valor inicial capitalizado + série de aportes no fim do mês
```

O marco `v0.5.4` entrega a projeção direta e uma linha do tempo curta. Cada
ponto separa capital colocado e juros do cenário; a visualização usa texto e
valor além de cor. O app não busca taxa, não sugere taxa padrão como adequada e
não chama o resultado de retorno esperado.

O marco `v0.5.5` reutiliza os mesmos fatores para duas perguntas:

- `calculateRequiredMonthlyContribution` resolve o aporte mensal de uma meta;
- `compareDelayedStart` mantém o valor inicial parado durante a espera e
  compara o mesmo horizonte final, explicitando aportes não realizados.

O marco `v0.5.6` completa a exploração:

- `adjustForInflation` desconta uma inflação também escolhida pela pessoa e
  mostra poder de compra no início do cenário;
- `simulateHabitRedirect` converte recorrência diária por 365/12, semanal por
  52/12 ou mensal diretamente, sem julgamento comportamental;
- `compareIntuitionChallenge` compara a mesma base contra +1 p.p. de taxa e
  +R$ 150 por mês, revelando o resultado somente depois do palpite.

`MoneyLabSession` vive em `App.tsx` para sobreviver à troca entre as quatro
abas, mas não possui adaptador de storage. Reiniciar o processo elimina valores,
ferramenta selecionada, inflação e palpite. O laboratório não toca SecureStore,
filesystem, histórico público, favoritos, carteira privada, importador B3,
snapshot ou rede. O modo discreto usa a mesma preferência efêmera para mascarar
campos e resultados monetários.

O corte consolidado `v0.5.6/15` passou por TypeScript, 51 testes de domínio,
16 de componentes, 4 contratos E2E e export Android/Hermes com 653 módulos. As
cinco ferramentas, a inflação e o desafio foram percorridos em 375×812,
430×932, 768×1024 e 844×390, sem overflow horizontal ou alvo interativo visível
abaixo de 44 px. Isso não substitui validação nativa, TalkBack, texto ampliado
ou os fluxos Maestro pausados.

O marco `v0.5.7` estende o mesmo domínio sem trocar a fórmula-base:

- `calculateDoublingTime` procura o primeiro mês em que o valor inicial dobra,
  separando o cenário com aportes daquele sem novos aportes;
- `calculateMilestoneTimeline` procura os marcos de R$ 10 mil, R$ 50 mil e
  R$ 100 mil somente dentro do horizonte escolhido;
- a régua usa anos inteiros de 1 a 50, com pontos tocáveis e botões menos/mais,
  sem biblioteca de gesto ou slider adicional.

O marco `v0.5.8` adiciona duas traduções locais. `calculateMonthlyYieldEquivalent`
usa a taxa mensal efetiva, nunca a divisão simples por 12. `simulateExtraContribution`
mantém o cenário-base e acrescenta um valor no início ou ao fim de cada ano;
isso não representa calendário de 13º, renda garantida ou produto.

O marco `v0.5.9` mantém a reserva fora da projeção de rendimento.
`calculateReserveJourney` divide o valor atual pelo gasto essencial digitado e,
quando existe aporte, calcula quantos meses inteiros faltam até a meta escolhida
de três, seis ou doze meses. A função não lê carteira nem define meta adequada.

O marco `v0.6.0` consolida a leitura:

- `compareContributionImpact` põe o mesmo valor inicial com e sem aportes;
- `compareAnnualCostDrag` trata custo como uma redução anual hipotética da taxa,
  limitada à própria taxa do cenário; não modela imposto ou produto;
- inflação e custo continuam fechados até ação explícita;
- `MoneyLabExpansionPanel` organiza os quatro caminhos adicionais sem criar aba.

Os campos novos pertencem ao mesmo `MoneyLabSession` de `App.tsx`. Trocar de
aba preserva a brincadeira; reiniciar o processo elimina ferramenta, valores,
meta, frequência e opções avançadas. Nenhum adaptador de storage, provider,
snapshot, carteira, rede ou telemetria participa dessa sequência.

O corte consolidado `v0.6.0/19` passou por TypeScript, 61 testes de domínio, 22
de componentes, 4 contratos E2E e export Android/Hermes com 654 módulos. As
quatro trilhas novas foram percorridas em 375×812, 430×932, 768×1024 e 844×390,
sem overflow horizontal ou alvo interativo visível abaixo de 44 px. Os marcos
`v0.5.7/16`, `v0.5.8/17` e `v0.5.9/18` não receberam builds EAS intermediários.
Nenhum Maestro ou gate físico foi executado.

O marco `v0.6.1` reduz a densidade sem criar navegação nova.
`MoneyLabIntentHub` grava em `MoneyLabSession` uma das famílias `basics`,
`explore` ou `life`; `ScenariosScreen` renderiza somente o painel escolhido.
As ferramentas preservadas continuam sendo os mesmos componentes e contratos.

O marco `v0.6.2` adiciona `simulateFlexibleContributionPlan`. A função recebe a
mesma `CompoundGrowthInput`, aplica o aumento escolhido ao aporte no início de
cada ano e zera apenas os meses da pausa. A comparação base continua vindo de
`simulateCompoundGrowth`; aporte pulado não é acumulado como dívida nem reposto.

O marco `v0.6.3` adiciona `compareCashAndInstallments`. A função soma parcelas e,
somente quando o total supera o preço à vista, resolve por busca binária a taxa
mensal que iguala o valor presente de parcelas ao fim de cada mês ao preço à
vista. O equivalente anual é efetivo. Quando o total parcelado não é maior, as
taxas retornam `null` em vez de inventar custo positivo.

O marco `v0.6.4` adiciona `simulateWithdrawalLongevity`. O laço converte a taxa
efetiva anual para equivalente mensal, credita o crescimento e realiza a
retirada no fim de cada mês. Quando a opção avançada está ligada, a retirada é
reajustada depois de cada doze meses completos. A função para no esgotamento ou
no horizonte de 1 a 50 anos e devolve no máximo cinco marcos de saldo.

`MoneyLifePanel` apresenta essas três contas sem acessar carteira, snapshot ou
provider. Entradas, família, pausa, parcelas, retiradas e inflação opcional
vivem na mesma sessão efêmera. Parcelamento não recomenda pagamento; duração do
saldo não define retirada segura. Tarifas, atraso, limite, imposto, volatilidade
e mudanças futuras de renda ou gastos ficam fora.

O corte consolidado `v0.6.3/22` passou por TypeScript, 66 testes de domínio, 30
de componentes, 4 contratos E2E e export Android/Hermes com 656 módulos. As
três famílias e as duas ferramentas cotidianas foram percorridas em 375×812,
430×932, 768×1024 e 844×390 com movimento reduzido, sem overflow horizontal ou
alvo interativo visível abaixo de 44 px. `v0.6.1/20` e `v0.6.2/21` não receberam
build EAS intermediário. Nenhum Maestro ou gate físico foi executado.

O corte `v0.6.4/23` passou por TypeScript, 70 testes de domínio, 33 de
componentes, 4 contratos E2E e export Android/Hermes com 656 módulos. A terceira
ferramenta cotidiana, inclusive inflação opcional, foi percorrida em 375×812,
430×932, 768×1024 e 844×390 com movimento reduzido. Documento, body e painel
mantiveram a largura do viewport; nenhum controle visível ficou abaixo de 44 px.
Nenhum preview EAS, Maestro ou gate físico foi executado.

### Fronteira implementada do contrato vivo `v1`

O snapshot transporta somente a leitura pública já calculada: versão do
schema, modo, datas, veredito, provas, disponibilidade das fontes e sinais com
efeitos por classe. Ele não transporta posições, valores ou identificadores da
carteira. Essa separação evita transformar um artefato público e versionável em
um canal acidental de dados pessoais.

`gerar_mobile_snapshot.py` lê somente os dois caches públicos versionados, sem
rede. O adaptador compõe `ResumoIntegrado`, `ResumoFocusSemanal`,
`LeituraCurva` e `LeituraConvergencia`, reutiliza os formatadores e efeitos
existentes e grava JSON ordenado por chave, com UTF-8, newline final e troca
atômica. O efeito de Curva por classe não existe nos motores aprovados; por
isso, o adaptador mantém esse mapa vazio em vez de inventar o elo.

No app, `snapshotProvider.ts` valida o JSON e escolhe fotografia viva ou demo.
Somente depois dessa escolha a camada local combina os efeitos públicos com a
carteira ativa, privada quando disponível ou sintética na demo. Schema público
ausente, desconhecido ou inválido degrada para a demo
explicitamente rotulada, sem derrubar a navegação. O documento público é
rejeitado se transportar `positions`, `amount` ou outra chave pessoal proibida.

### Fronteira implementada do contrato privado `v1`

```text
SNAPSHOT PÚBLICO v1               CARTEIRA PRIVADA v1
sinais · fontes · evidências      posições · classes · valores
          │                                  │
          │                    AES-256-GCM + cofre nativo
          └──────────────────┬───────────────┘
                             ▼
                    COMPOSIÇÃO EM MEMÓRIA
                    Hoje · Carteira · Cenários
```

`src/domain/privatePortfolio.ts` define um documento versionado, estrito e
limitado a 100 posições. Nome, classe, identificador e valor são validados antes
de qualquer gravação. O contrato público continua proibindo chaves pessoais;
não existe migração ou ampliação de `liveSnapshot.json` para transportar
carteira.

`src/storage/securePortfolioStorage.ts` implementa a fronteira nativa:

- gera uma chave AES de 256 bits e guarda somente sua codificação no
  `expo-secure-store`;
- usa `WHEN_UNLOCKED_THIS_DEVICE_ONLY` no Keychain e armazenamento protegido
  pelo Android Keystore no Android;
- cifra o JSON com AES-GCM e contexto autenticado fixo;
- grava bytes em arquivo temporário dentro de `Paths.document` e move para o
  destino com substituição, evitando aceitar gravação parcial;
- rejeita chave ausente, autenticação inválida, ciphertext corrompido ou schema
  desconhecido e não recua silenciosamente para a demo;
- apaga arquivo e chave somente depois de confirmação explícita do usuário.

O cofre guarda uma chave pequena; o documento financeiro fica cifrado no
sistema de arquivos do app. Biometria não foi ativada neste incremento para não
confundir criptografia em repouso com autenticação do usuário. Backup/restauração
entre aparelhos não é prometido: uma carteira sem a chave local falha fechada e
oferece reset explícito.

### Fronteira implementada da importação B3

```text
DOCUMENT PICKER NATIVO
XLSX escolhido pela pessoa
        │  cópia temporária privada · até 5 MB
        ▼
LEITOR B3 MÍNIMO
ZIP/XML em memória · abas permitidas · limites estruturais
        │  ativo · classe · valor
        ▼
PRÉVIA SANITIZADA
contagens · total · exclusões · posições
        │  confirmação explícita
        ▼
CARTEIRA PRIVADA v1
AES-256-GCM no aparelho
```

`src/storage/b3DocumentPicker.ts` abre a interface nativa, exige XLSX, lê a
cópia criada em `Paths.cache` e a apaga antes de devolver a prévia. O original
do provedor de documentos não é alterado. Web continua sem carteira privada e
sem importação.

`src/domain/b3Import.ts` não é um motor financeiro novo. Ele porta somente o
adaptador de formato já testado em `b3_importacao.py`: reconhece as seis abas
esperadas, ignora a dimensão `A1` incorreta, extrai os campos mínimos,
classifica pelas mesmas regras cobertas no mobile e consolida duplicidades.
Cripto e ouro não são forçados para classes incorretas; entram na contagem de
linhas não suportadas e ficam fora da gravação.

O parser extrai somente entradas OOXML conhecidas e limita arquivo comprimido,
tamanho expandido, XML individual, entradas, shared strings, linhas, células,
posições e valor. Arquivos macro-enabled, DTD/entidade XML, vínculos fora de
`xl/worksheets/` ou contrato privado inválido falham fechados. A carteira atual
só muda depois da prévia e da confirmação de substituição.

## Privacidade e guardrails

- nenhuma conta, CPF, instituição, posição real ou planilha foi usada;
- a carteira demo é sintética e versionável;
- valores reais ficam no aparelho por padrão no contrato privado `v1`;
- sincronização, Open Finance ou backend exigirão consentimento explícito,
  autenticação, criptografia, revogação e revisão de segurança;
- o app descreve sensibilidade e evidência, nunca compra, venda ou promessa;
- qualquer integração regulada será proposta técnica, com validação final das
  áreas jurídica e de compliance aplicáveis.

## Relação com o FocusLens Embedded

O app móvel é o cliente de referência da futura camada institucional, mas não
é a própria integração bancária. O roadmap aprovado preserva esta fronteira e,
depois da maturidade móvel, adiciona Intelligence API, receipt auditável,
Exposure Adapter privado, SDK white-label e Governance Studio.

O snapshot público `v1` não será ampliado para transportar carteira. Em uma
instituição, sinais públicos e posições consentidas só se encontram depois da
fronteira privada. A arquitetura-alvo está em
[`ARQUITETURA_INSTITUCIONAL.md`](ARQUITETURA_INSTITUCIONAL.md); tese, piloto e
métricas estão em [`ESTRATEGIA_INSTITUCIONAL.md`](ESTRATEGIA_INSTITUCIONAL.md).
Esses componentes ainda não estão implementados e não entram no development
build atual.

## Roadmap técnico imediato

1. **concluído:** snapshot JSON público e versionado a partir dos motores
   Python, sem carteira, com schema e teste de compatibilidade;
2. **concluído:** provider somente leitura com fallback local explícito;
3. **pausado após evidência parcial:** configuração EAS/dev client, safe areas, rotação,
   identificadores, splash e perfis internos concluída; APKs Android
   `development` e `preview` gerados e instalados no POCO X8 Pro, com fluxo
   principal/offline aprovado, acessibilidade física pendente e rota iOS em
   `VALIDACAO_DEVELOPMENT_BUILD.md`;
4. **implementado; CL-02 a CL-10 aprovados:** carteira local editável e
   criptografada, sem nuvem por padrão; acessibilidade física pendente;
5. **implementado; BI-01 a BI-03 aprovados:** importação B3 sanitizada para o
   mesmo contrato privado; restante do ciclo físico pendente;
6. **implementado localmente em `v0.4.1`:** recorte pessoal, distribuição por
   classe, cobertura honesta e revelação progressiva;
7. **implementado localmente em `v0.4.2`:** modo discreto entre abas e resumo
   de Cenários por tom/cobertura; preview pendente;
8. **implementado localmente em `v0.4.3`:** Home centrada no recorte pessoal,
   maior posição derivada e ação principal contextual; preview pendente;
9. **implementado e empacotado em `v0.4.4`:** entrada pessoal antes da carteira
    fictícia, com B3 principal e alternativa manual; preview EAS sucedido pelo
    corte consolidado `v0.5.2/11`;
10. **implementado localmente em `v0.5.0`:** alertas explicáveis, favoritos e
    comparação entre até oito fotografias públicas, sem carteira no histórico;
11. **implementado localmente em `v0.5.1`:** simulador de aportes por classe,
    sem persistência, retorno previsto, produto ou ordem;
12. **implementado e empacotado em `v0.5.2`:** testes de componentes e contratos
    E2E; preview Android build `11` instalado por relato e fluxos Maestro
    preparados, mas ainda não executados no aparelho;
13. **implementado localmente em `v0.5.3`:** revisão guiada da semana e
    Entenda contextual, somente com estado de sessão e contratos existentes;
14. **implementado localmente em `v0.5.4`:** crescimento composto com valor
    inicial, aportes, taxa escolhida, prazo e decomposição do resultado;
15. **implementado localmente em `v0.5.5`:** meta ao contrário e comparação
    entre começar agora ou depois;
16. **implementado localmente em `v0.5.6`:** inflação opcional, hábito
    recorrente e desafio de intuição, todos somente em sessão;
17. **implementado localmente em `v0.5.7`:** dobra, marcos e régua temporal;
18. **implementado localmente em `v0.5.8`:** equivalente mensal e aporte extra;
19. **implementado localmente em `v0.5.9`:** caminho da reserva sem rendimento;
20. **implementado localmente em `v0.6.0`:** comparação de aporte, inflação e
    custo anual hipotético sob revelação progressiva;
21. **implementado localmente em `v0.6.1`:** seletor por intenção e uma família
    do laboratório por vez;
22. **implementado localmente em `v0.6.2`:** aporte com aumento anual e pausa
    opcional, sem dívida ou reposição automática;
23. **implementado localmente em `v0.6.3`:** comparação à vista/parcelado e taxa
    implícita sob convenção explícita;
24. **implementado localmente em `v0.6.4`:** duração de saldo sob retiradas
    mensais e reajuste anual opcional, somente na sessão;
25. executar os fluxos E2E em estado seguro e fechar os gates físicos pendentes;
26. somente depois, avaliar autenticação e integrações bancárias/Open Finance.

## Gate de produção

O corte atual é uma demonstração funcional, não uma entrega de loja. Antes de
produção são obrigatórios: testes de componentes, E2E em Android/iOS, leitura
por screen reader, armazenamento seguro, política de privacidade, threat model,
telemetria sem dado financeiro, tratamento offline, assinatura de builds e
zero vulnerabilidade alta ou crítica. A auditoria atual do npm encontrou zero
alta/crítica e 11 moderadas transitivas no toolchain Expo; não foi aplicado
`audit fix --force`, pois a sugestão faria downgrade incompatível de pacotes do
toolchain, inclusive do Expo.

### Distribuição nativa preparada em 2026-08-28

- `eas.json` possui development client interno em APK, simulador iOS e preview
  interno para abertura offline;
- `app.json` usa identificadores `com.raulsallesr.focuslens`, scheme
  `focuslens`, orientação adaptável e plugin de splash aceito pelo SDK 57;
- `App.tsx` usa `SafeAreaProvider` e aplica os quatro lados, inclusive gesto
  inferior e recortes laterais em paisagem;
- controles que estavam em 44–46 px foram elevados para 48 px e os cabeçalhos
  podem quebrar de forma controlada com texto ampliado;
- Expo Doctor aprovou `21/21` checks e o export Hermes aprovou 603 módulos;
- `@raulsallesr/focuslens-br` foi vinculado ao `projectId` público e os builds
  `development`/`preview` terminaram com o mesmo fingerprint do commit
  `60fa378`;
- development e preview foram instalados no POCO X8 Pro; quatro abas, snapshot
  e abertura em modo avião foram aprovados;
- rotação, safe areas em paisagem e botão Voltar foram aprovados no POCO X8
  Pro com Android 16 (`BP2A.250605.031.A3`); TalkBack, texto ampliado e alvos de
  toque permanecem pendentes e pausados;
- a evidência operacional está em `VALIDACAO_DEVELOPMENT_BUILD.md`.

### Armazenamento nativo preparado em 2026-08-28

- `expo-crypto ~57.0.2`, `expo-file-system ~57.0.6` e
  `expo-secure-store ~57.0.2` foram instalados pela resolução compatível do Expo;
- o plugin do SecureStore configura as exclusões de Android Auto Backup e não
  declara permissão de Face ID, pois biometria não é usada neste corte;
- a carteira demo nunca é persistida automaticamente: a troca acontece somente
  ao salvar a primeira posição local;
- edição, exclusão e reset atualizam o cofre; as demais telas recebem a carteira
  privada somente por composição em memória;
- a bancada web continua explicitamente em demonstração;
- TypeScript, 20 testes, export web e bundle Android/Hermes com 633 módulos
  passaram; o preview nativo `67b97c57-ce20-4cb6-8c21-570c4742762e` foi gerado
  para o commit `9308f02`. CL-02 a CL-10 foram depois aprovados no `v0.4.0`.
- o gate físico do cofre está em `VALIDACAO_CARTEIRA_LOCAL.md`.

### Importação B3 nativa preparada em 2026-08-28

- `expo-document-picker ~57.0.1` abre o seletor nativo e `fflate 0.8.3`
  descomprime somente o subconjunto OOXML permitido;
- TypeScript, 25 testes, export web, Expo Doctor `21/21` e bundle
  Android/Hermes com 640 módulos passaram;
- a auditoria da árvore de produção encontrou zero vulnerabilidade; a árvore
  completa mantém 11 moderadas transitivas do toolchain, sem alta ou crítica;
- o preview `c7695638-2f38-42a4-af07-92303f2a5ce0`, commit `c6bb875` e
  fingerprint `4df3790bd18465bb8a429b23f9814aabf1ac6dc8` terminou `FINISHED`;
- o APK `v0.4.0`, build `4`, expira em 2026-09-11; BI-01 a BI-03 foram
  aprovados e BI-04 a BI-13 continuam pendentes em
  `VALIDACAO_IMPORTACAO_B3.md`.
