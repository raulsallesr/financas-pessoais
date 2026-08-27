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

## Estado do corte `mobile v0.2`

O diretório `mobile/` contém a experiência completa de navegação e consome o
snapshot público `v1`. A fotografia sintética em `src/data/demoSnapshot.ts`
permanece como fallback explícito e nunca é confundida com dado vivo.

O domínio TypeScript faz apenas operações locais necessárias à experiência:

- soma e peso da carteira sintética;
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
carteira sintética. Schema ausente, desconhecido ou inválido degrada para a demo
explicitamente rotulada, sem derrubar a navegação. O documento público é
rejeitado se transportar `positions`, `amount` ou outra chave pessoal proibida.

## Privacidade e guardrails

- nenhuma conta, CPF, instituição, posição real ou planilha foi usada;
- a carteira demo é sintética e versionável;
- valores reais deverão ficar no aparelho por padrão;
- sincronização, Open Finance ou backend exigirão consentimento explícito,
  autenticação, criptografia, revogação e revisão de segurança;
- o app descreve sensibilidade e evidência, nunca compra, venda ou promessa;
- qualquer integração regulada será proposta técnica, com validação final das
  áreas jurídica e de compliance aplicáveis.

## Roadmap técnico imediato

1. **concluído:** snapshot JSON público e versionado a partir dos motores
   Python, sem carteira, com schema e teste de compatibilidade;
2. **concluído:** provider somente leitura com fallback local explícito;
3. gerar e instalar um development build próprio para Android e preparar a
   mesma rota no iOS;
4. criar carteira local editável e criptografada, sem nuvem por padrão;
5. portar a importação B3 de forma sanitizada para um fluxo móvel seguro;
6. adicionar alertas explicáveis, favoritos e comparação entre fotografias;
7. somente depois, avaliar autenticação e integrações bancárias/Open Finance.

## Gate de produção

O corte atual é uma demonstração funcional, não uma entrega de loja. Antes de
produção são obrigatórios: testes de componentes, E2E em Android/iOS, leitura
por screen reader, armazenamento seguro, política de privacidade, threat model,
telemetria sem dado financeiro, tratamento offline, assinatura de builds e
zero vulnerabilidade alta ou crítica. A auditoria atual do npm encontrou zero
alta/crítica e dez moderadas transitivas no toolchain Expo; não foi aplicado
`audit fix --force`, pois a sugestão do npm faria downgrade incompatível.
