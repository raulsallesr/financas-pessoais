# Arquitetura-alvo — FocusLens Embedded

**Status:** arquitetura de referência aprovada; nenhum componente institucional
descrito aqui existe em produção.

**Fronteira atual implementada:** `docs/ARQUITETURA_MOBILE.md`.

**Tese e roadmap comercial:** `docs/ESTRATEGIA_INSTITUCIONAL.md`.

## 1. Objetivo

Permitir que uma instituição incorpore a inteligência explicável do FocusLens
em seus próprios canais sem:

- duplicar os motores financeiros na interface;
- transportar carteira no snapshot público;
- depender de uma caixa-preta generativa para emitir o veredito;
- misturar explicação educacional com recomendação de produto;
- perder a capacidade de reproduzir uma decisão passada.

## 2. Princípios

1. **Motor único:** os contratos Python continuam como fonte dos cálculos.
2. **Dado no menor domínio:** posição e valor permanecem na fronteira privada.
3. **Consentimento verificável:** acesso exige finalidade, escopo, validade e
   revogação explícitos.
4. **Explicação como contrato:** toda saída contém evidência, limite e versão.
5. **Política fora do motor:** o banco decide quem recebe, quando e por qual
   canal sem alterar o cálculo financeiro.
6. **Reprodução antes de automação:** nenhuma decisão em produção pode existir
   sem receipt auditável.
7. **Degradação segura:** dado ausente ou incompatível reduz funcionalidade; não
   gera uma leitura inventada.
8. **Regulação por validação competente:** esta arquitetura é proposta técnica,
   não conclusão jurídica ou regulatória.

## 3. Visão lógica

```text
FONTES PÚBLICAS
BACEN · Tesouro · SGS · fontes autorizadas
        │
        ▼
ADAPTADORES DE I/O
cache · validação · disponibilidade · proveniência
        │
        ▼
MOTORES PYTHON FOCUSLENS
Focus · Curva · Convergência · Radar
        │
        ▼
INTELLIGENCE API ───────────────► RECEIPT PÚBLICO
sinal · evidência · fonte          regra · versão · limite
        │
        │ cruza a fronteira institucional sem carteira
        ▼
┌──────────────── AMBIENTE PRIVADO DA INSTITUIÇÃO ────────────────┐
│ POSIÇÕES CONSENTIDAS ─► EXPOSURE ADAPTER                        │
│                              │                                  │
│                              ▼                                  │
│ POLÍTICA INSTITUCIONAL ─► ALERT DECISION ─► APP/WEB/ASSESSORIA  │
│          ▲                   │                                  │
│          │                   ▼                                  │
│ GOVERNANCE STUDIO ◄──── AUDIT LOG / REPLAY                      │
└─────────────────────────────────────────────────────────────────┘
```

O fluxo público termina no receipt do sinal. A carteira só entra depois, em
ambiente controlado pela instituição. Uma instalação gerenciada que precise de
outro desenho deverá provar minimização, base e finalidade do tratamento,
criptografia, segregação e retenção antes do piloto.

## 4. Componentes

| Componente | Responsabilidade | Não pode fazer |
|---|---|---|
| Adaptadores públicos | Coletar, validar, datar e armazenar fontes permitidas | Inferir dado ausente ou aceitar fonte não atribuída |
| Motores FocusLens | Produzir sinais determinísticos e explicáveis | Ler carteira, consentimento ou catálogo do banco |
| Intelligence API | Distribuir contratos versionados e receipts | Receber posição em endpoint público |
| Exposure Adapter | Relacionar sinais a exposições consentidas | Selecionar produto ou executar ordem |
| Policy Engine | Aplicar elegibilidade, frequência e canal aprovados | Alterar o cálculo do sinal |
| Governance Studio | Aprovar, versionar, simular, interromper e reproduzir | Editar histórico de decisão já emitida |
| SDK white-label | Renderizar explicação nos canais da instituição | Reimplementar fórmula financeira |
| Telemetria | Medir saúde, utilidade e falha de forma agregada | Registrar posição, valor ou identificador financeiro bruto |

## 5. Contratos propostos

Os nomes abaixo são de referência. A primeira implementação deve fechar os
schemas com exemplos e testes de compatibilidade antes de criar endpoints.

### 5.1 `MarketSignalReceipt`

Contrato público produzido pela Intelligence API:

```text
schemaVersion
signalId
engineVersion
ruleVersion
generatedAt
asOf
title
movement
evidence[]
sources[]
exposuresByClass{}
horizon
limits[]
changeConditions[]
```

Não admite posição, quantidade, valor, conta, documento, instituição do cliente
ou identificador pessoal. É a evolução institucional do princípio já aplicado
ao snapshot móvel `v1`, não uma substituição incompatível desse artefato.

### 5.2 `PortfolioContextInternal`

Contrato privado da instituição:

```text
subjectReference pseudonimizada
consentReference
purpose
validUntil
positions[] com classe e exposição mínima necessária
```

Esse contrato não é persistido no repositório, não aparece em exemplos reais e
não atravessa a fronteira pública. Identificadores e campos serão definidos com
privacy engineering e segurança da instituição.

### 5.3 `AlertDecisionReceipt`

Resultado da combinação entre sinal, exposição e política:

```text
decisionId
marketSignalReceiptId
policyVersion
contentVersion
eligibilityReason
relatedExposureClasses[]
channel
decidedAt
deliveryStatus
```

O receipt guarda referências e motivos, não a carteira bruta. Retenção,
imutabilidade e acesso serão políticas formais do banco.

## 6. Planos separados

### Plano de dados

- fontes públicas e autorizadas;
- adaptadores, caches e proveniência;
- motores e contracts;
- contexto de exposição dentro da fronteira privada;
- receipts de decisão.

### Plano de controle

- identidade, papéis e segregação;
- consentimento e finalidade;
- configuração e aprovação de políticas;
- distribuição de versões;
- kill switch;
- auditoria e replay.

Uma mudança no plano de controle não pode reescrever o resultado histórico do
plano de dados. Uma nova regra gera nova versão e passa novamente pelos gates.

## 7. Identidade e consentimento

A instituição continua dona da identidade do cliente. O FocusLens não criará um
cadastro paralelo no piloto.

Quando houver integração Open Finance, o desenho deve:

- usar a implementação FAPI/OAuth/OIDC e os certificados exigidos pelo arranjo;
- tratar token e consentimento como objetos distintos;
- verificar escopo, finalidade, validade e revogação antes do acesso;
- interromper o uso quando o consentimento deixar de ser válido;
- manter evidência da versão e da finalidade apresentadas;
- passar pela certificação e validação aplicáveis à instituição participante.

Open Finance não é dependência da primeira prova de valor. O piloto inicial usa
dados que o próprio banco já mantém e está autorizado a processar para a
finalidade aprovada.

## 8. Segurança mínima

### Mobile e SDK

- OWASP MASVS/MASTG como baseline;
- armazenamento seguro e ausência de segredo em bundle;
- pinning ou controles de transporte conforme threat model;
- proteção de logs, screenshots e deep links conforme sensibilidade;
- assinatura, proveniência e atualização controlada;
- E2E em Android/iOS, acessibilidade e tratamento offline.

### API e backend

- OWASP ASVS e threat model versionado;
- TLS, autenticação forte e autorização por menor privilégio;
- gestão de segredos por cofre;
- criptografia em repouso;
- allowlist e validação estrita de schema;
- proteção contra replay, abuso e excesso de requisição;
- logs estruturados sem dado financeiro bruto;
- SAST, SCA, SBOM, análise de imagem e dependências bloqueantes;
- artefatos assinados e promoção imutável entre ambientes.

### Organização

- inventário e classificação de dados;
- papéis de operação, aprovação e auditoria separados;
- gestão de fornecedor e subcontratado;
- resposta a incidente e comunicação;
- continuidade, backup e recuperação testados;
- revisão periódica de acesso e vulnerabilidade.

## 9. Observabilidade e SLO

Antes do piloto, cada serviço deverá expor métricas técnicas sem posição ou
valor financeiro:

- disponibilidade por fonte e idade da fotografia;
- latência e taxa de erro por contrato;
- rejeição de schema e uso de fallback;
- decisões geradas, suprimidas e interrompidas por política;
- falhas de entrega por canal;
- versão de motor, regra, política e conteúdo em uso;
- integridade e atraso da trilha de auditoria.

Metas numéricas de SLO só serão fixadas depois de medir o sandbox. A proposta
comercial não deve prometer disponibilidade que ainda não foi testada.

## 10. Governança de regra

Toda alteração com efeito sobre uma explicação ou alerta exige:

1. motivo e responsável;
2. diff legível da regra ou conteúdo;
3. exemplos sintéticos esperados;
4. replay contra conjunto de regressão;
5. aprovação conforme alçada;
6. versão imutável;
7. implantação gradual e rollback;
8. monitoramento de qualidade depois da ativação.

Uma interface generativa futura poderá resumir receipts aprovados, mas não será
a fonte do sinal. Ela deverá citar as evidências, respeitar limites e recusar
recomendação fora da política.

## 11. Gates por estágio

### Sandbox

- contratos fechados e exemplos apenas sintéticos;
- compatibilidade testada;
- nenhuma carteira no plano público;
- threat model inicial;
- trilha completa de uma decisão demonstrável.

### Piloto restrito

- identidade e consentimento integrados;
- RBAC, auditoria, replay e kill switch;
- E2E dos canais utilizados;
- observabilidade e runbooks;
- segurança e privacidade aprovadas pela instituição;
- métricas e grupo de controle definidos.

### Produção

- escala, carga, resiliência e recuperação testadas;
- vulnerabilidade alta ou crítica bloqueante igual a zero;
- SLO e suporte contratados;
- cadeia de software e artefatos assinados;
- política de retenção e descarte implementada;
- avaliações jurídica, compliance, segurança e risco concluídas;
- piloto atingiu os critérios comerciais acordados.

## 12. Decisões arquiteturais fechadas

- o snapshot móvel público `v1` continua sem carteira;
- os motores Python não conhecem identidade, consentimento ou catálogo;
- a primeira integração usa dados internos do banco, não Open Finance;
- explicação e recomendação comercial são camadas distintas;
- a implantação preferencial é dentro da fronteira privada da instituição;
- toda decisão em produção deve ser reproduzível por receipt e versões;
- IA generativa, se adotada, resume evidência governada e não cria o veredito.

## 13. Questões que serão fechadas antes da Fase B

- protocolo síncrono, assíncrono ou híbrido da Intelligence API;
- granularidade mínima permitida no contexto de exposição;
- tecnologia e retenção da trilha imutável;
- matriz de papéis do Governance Studio;
- SLO medido no sandbox;
- suporte inicial a React Native nativo, web ou ambos;
- modelo de isolamento por instituição;
- requisitos de portabilidade entre VPC privada e serviço gerenciado.
