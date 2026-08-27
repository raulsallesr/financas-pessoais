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
        ▼  próximo incremento: snapshot versionado / API somente leitura
CONTRATO MÓVEL
veredito · sinais · efeitos por classe · data · fonte · limites
        │
        ▼
APP REACT NATIVE
Hoje · Carteira · Cenários · Entenda
```

Os motores Python continuam como fonte das leituras públicas. O app não deve
reimplementar mediana, relevância do Focus, comparação D-5/D-21 ou estados de
convergência. A futura ponte entregará somente contratos já calculados.

## Estado do corte `mobile v0.1`

O diretório `mobile/` já contém a experiência completa de navegação e usa uma
fotografia sintética em `src/data/demoSnapshot.ts`. Essa fotografia existe para
validar a jornada e nunca deve ser confundida com dado vivo.

O domínio TypeScript faz apenas operações locais necessárias à experiência:

- soma e peso da carteira sintética;
- filtro de posições por classe;
- junção entre o efeito já declarado no snapshot e as posições relacionadas;
- sensibilidade educacional discreta a choques de juros.

A sensibilidade móvel é uma demonstração própria e está rotulada como tal. Ela
não substitui `curva_cenarios.py`, não calcula preço ou retorno e não entra nos
motores aprovados da `v2.0`.

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

1. gerar um snapshot JSON versionado a partir dos motores Python, com schema e
   teste de compatibilidade;
2. trocar o provider demo por um provider somente leitura com fallback local;
3. criar carteira local editável e criptografada, sem nuvem por padrão;
4. portar a importação B3 de forma sanitizada para um fluxo móvel seguro;
5. adicionar alertas explicáveis, favoritos e comparação entre fotografias;
6. somente depois, avaliar autenticação e integrações bancárias/Open Finance.

## Gate de produção

O corte atual é uma demonstração funcional, não uma entrega de loja. Antes de
produção são obrigatórios: testes de componentes, E2E em Android/iOS, leitura
por screen reader, armazenamento seguro, política de privacidade, threat model,
telemetria sem dado financeiro, tratamento offline, assinatura de builds e
zero vulnerabilidade alta ou crítica. A auditoria atual do npm encontrou zero
alta/crítica e dez moderadas transitivas no toolchain Expo; não foi aplicado
`audit fix --force`, pois a sugestão do npm faria downgrade incompatível.
