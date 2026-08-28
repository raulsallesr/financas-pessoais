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

## Estado do corte `mobile v0.4`

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
- filtro de posições por classe;
- junção entre o efeito já declarado no snapshot e as posições relacionadas;
- sensibilidade educacional discreta a choques de juros.

A sensibilidade móvel é uma demonstração própria e está rotulada como tal. Ela
não substitui `curva_cenarios.py`, não calcula preço ou retorno e não entra nos
motores aprovados da `v2.0`.

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
3. **em andamento:** configuração EAS/dev client, safe areas, rotação,
   identificadores, splash e perfis internos concluída; APKs Android
   `development` e `preview` gerados e instalados no POCO X8 Pro, com fluxo
   principal/offline aprovado, acessibilidade física pendente e rota iOS em
   `VALIDACAO_DEVELOPMENT_BUILD.md`;
4. **implementado; validação física pendente:** carteira local editável e
   criptografada, sem nuvem por padrão;
5. **implementado; validação física pendente:** importação B3 sanitizada para o
   mesmo contrato privado;
6. adicionar alertas explicáveis, favoritos e comparação entre fotografias;
7. adicionar testes de componentes e E2E Android/iOS;
8. somente depois, avaliar autenticação e integrações bancárias/Open Finance.

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
  Pro; versão do Android, TalkBack, texto ampliado e alvos de toque permanecem
  pendentes;
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
  para o commit `9308f02` e aguarda instalação no aparelho.
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
- o APK `v0.4.0`, build `4`, expira em 2026-09-11 e aguarda BI-01 a BI-13 em
  `VALIDACAO_IMPORTACAO_B3.md`.
