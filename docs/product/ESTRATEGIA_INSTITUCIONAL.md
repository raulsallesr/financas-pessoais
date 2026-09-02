# FocusLens Embedded — estratégia institucional

**Status:** direção aprovada em 2026-08-27; produto institucional ainda não
implementado.

**Próximo passo técnico do repositório:** concluir os gates físicos da Etapa 5
antes de iniciar qualquer implementação da Etapa 6.

**Documento complementar:** `docs/architecture/ARQUITETURA_INSTITUCIONAL.md`.

## 1. Decisão de produto

O FocusLens seguirá duas trilhas que compartilham os mesmos contratos, mas têm
finalidades diferentes:

1. **FocusLens Mobile:** produto pessoal e cliente de referência dos motores;
2. **FocusLens Embedded:** camada institucional de inteligência financeira
   explicável, incorporável a app, internet banking e plataforma de assessoria.

O produto institucional não será vendido como um painel de indicadores nem
como um previsor de mercado. A proposta é ajudar uma instituição a responder,
de forma personalizada e auditável:

> O que mudou, qual evidência sustenta a leitura, onde isso encosta na carteira
> consentida e o que o dado não permite concluir?

O app móvel atual permanece como laboratório de experiência e implementação de
referência. Ele não será acoplado diretamente a sistemas bancários e não
receberá atalhos de autenticação, consentimento ou sincronização antes dos gates
documentados neste roadmap.

## 2. Por que uma instituição compraria

Uma instituição não compra o FocusLens apenas pelos dados públicos ou pelas
telas. Ela compra quatro resultados possíveis:

- **engajamento com contexto:** transformar movimentos abstratos de mercado em
  explicações ligadas ao que o cliente realmente possui;
- **retenção e relacionamento:** criar uma razão útil para o cliente retornar ao
  canal sem incentivar giro ou risco;
- **eficiência operacional:** reduzir o tempo de gerentes, assessores e suporte
  gasto explicando por que uma carteira pode ter sido afetada;
- **governança da comunicação:** reproduzir qual regra, evidência, versão e texto
  deram origem a cada explicação ou alerta.

O gatilho de compra será a combinação de valor comprovado, baixo risco de
integração e capacidade de auditoria. Qualidade visual sozinha não atende esse
critério.

## 3. Ativos existentes e lacunas

| Dimensão | Ativo existente | Lacuna institucional |
|---|---|---|
| Inteligência | Motores determinísticos de Focus, Curva, convergência e Radar | API estável, versionamento de regra e operação contínua |
| Explicabilidade | Sinal → Evidência → Exposição → Limite | Recibo auditável por decisão e texto aprovado pelo banco |
| Contrato | Snapshot público `v1`, validado e sem carteira | Contratos privados para exposição, alerta e auditoria |
| Privacidade | Carteira separada dos motores e demo sintética | Consentimento, revogação, criptografia e políticas de retenção |
| Interface | React Native Android/iOS e experiência de referência | SDK white-label e integração aos canais existentes |
| Qualidade | Testes Python e TypeScript; fallback explícito | E2E, carga, resiliência, segurança e compatibilidade contratual |
| Operação | Atualização automatizada dos caches públicos | Observabilidade, SLO, incidentes, continuidade e suporte |
| Comercial | Tese de uso clara | Piloto controlado, KPIs, referência institucional e receita recorrente |
| Propriedade intelectual | Código próprio, fontes atribuídas e licença MIT no projeto de referência | Titularidade e licença próprias para a implementação institucional |

### Fronteira de publicação

O app de referência, os motores educacionais e os contratos públicos deste
repositório usam a licença MIT. Isso permite estudar e reutilizar o projeto
público atual, mas não antecipa a forma de distribuição de uma futura
implementação institucional.

Intelligence API, Exposure Adapter, SDK, console e operação Embedded terão
escopo e repositório próprios, privados por padrão até decisão comercial
expressa. Nenhum código institucional futuro recebe a licença deste repositório
automaticamente.

## 4. Produto institucional-alvo

### 4.1 FocusLens Intelligence API

Serviço headless que expõe apenas contratos calculados e versionados pelos
motores Python. A API deve:

- conservar os motores como fonte única dos cálculos;
- publicar schema, versão do motor, data-base, fontes, evidências e limites;
- aceitar somente contexto mínimo e explicitamente definido;
- rejeitar dado pessoal em contratos públicos;
- ser distribuída com OpenAPI e exemplos sintéticos;
- permitir execução dentro da VPC ou infraestrutura da instituição.

### 4.2 Exposure Adapter

Componente executado dentro da fronteira de confiança da instituição. Ele
relaciona o sinal público às classes e posições da carteira consentida sem
devolver a carteira bruta ao plano público.

O adaptador não escolhe produto, não executa ordem e não transforma taxa de
título em previsão pura. Seu resultado é uma exposição explicada, não uma
recomendação.

### 4.3 Explainable Portfolio Alerts

Alertas baseados em mudança relevante, sempre acompanhados de um recibo com:

- evento e data observados;
- fontes e evidências;
- regra, limiar e versão aplicados;
- exposições relacionadas;
- intensidade e horizonte declarados;
- limitações e condições de mudança;
- texto aprovado e canal de entrega;
- identificador que permita reproduzir a decisão.

O primeiro caso de uso comercial será:

> “Algo relevante mudou. Estas partes da sua carteira são sensíveis a isso.
> Veja a evidência, os limites e por que a relação foi feita.”

### 4.4 Governance Studio

Console institucional para:

- habilitar ou interromper sinais e alertas;
- configurar limiares por segmento autorizado;
- aprovar textos e versões;
- simular o alcance de uma regra com dados sintéticos ou agregados;
- reproduzir uma decisão passada;
- acompanhar falso positivo, silêncio excessivo e reclamações;
- aplicar kill switch;
- exportar trilha de auditoria.

Esse plano de controle é o principal diferencial defensável do produto. Dados
públicos e telas podem ser copiados; uma biblioteca governada de relações entre
eventos, evidências e exposições, acompanhada de resultados reais, é mais
difícil de reproduzir.

### 4.5 SDK white-label

Componentes incorporáveis para Android/iOS, web e, quando houver demanda real,
Flutter. O SDK deve permitir à instituição controlar marca, tipografia, tokens,
acessibilidade, navegação e textos aprovados sem duplicar regra financeira.

### 4.6 Advisor Copilot — fase posterior

Visão para gerente ou assessor explicar movimentos, identificar clientes com
exposição relevante e reutilizar conteúdo aprovado. Qualquer sugestão de
produto ou próxima melhor ação ficará em uma camada separada, governada pelas
políticas da instituição e validada pelas áreas jurídica e de compliance.

## 5. Jornada principal

1. Um motor identifica uma mudança relevante usando fontes públicas.
2. A Intelligence API publica um sinal versionado e seu recibo de evidência.
3. Dentro do ambiente do banco, o Exposure Adapter verifica quais exposições
   consentidas se relacionam ao sinal.
4. A política institucional decide se existe contexto suficiente para explicar
   ou alertar.
5. O cliente recebe a explicação no canal do banco.
6. A decisão fica reproduzível sem gravar a carteira no contrato público.
7. Telemetria agregada mede utilidade, silêncio, abandono e reclamações sem
   registrar valores financeiros em analytics.

## 6. Modelo de implantação

Ordem de preferência para um piloto:

1. **VPC ou ambiente privado da instituição:** motores, adaptador e plano de
   controle operam dentro da fronteira do banco;
2. **serviço gerenciado com dados minimizados:** somente sinais públicos e
   contexto pseudonimizado estritamente necessário atravessam a fronteira;
3. **processamento local no aparelho:** adequado à carteira pessoal, mas com
   menor capacidade institucional de governança e operação.

O primeiro piloto deve usar posições que a própria instituição já mantém. Open
Finance amplia a visão para contas externas depois que segurança, consentimento
e valor do caso interno estiverem demonstrados.

## 7. Pacote comercial

O formato inicial será licenciamento B2B, não venda imediata do código-fonte:

- implantação e integração;
- licença anual da plataforma;
- faixa de clientes ativos ou volume de decisões;
- suporte, operação e evolução contratados;
- opção de VPC privada ou instalação dedicada;
- SDK e console de governança incluídos conforme o pacote.

Uma aquisição do produto ou da empresa exigiria, além da tecnologia:

- propriedade intelectual e licenças sem ambiguidade;
- referências institucionais em produção;
- receita recorrente e retenção comprovadas;
- baixa dependência de uma única instituição;
- base histórica de regras, resultados e aprendizado operacional;
- documentação de segurança e continuidade compatível com due diligence.

## 8. Piloto institucional

### 8.1 Hipótese

Uma explicação curta, personalizada e auditável aumenta a compreensão e o
retorno ao canal, ao mesmo tempo que reduz o esforço para explicar movimentos
de mercado, sem elevar reclamações ou induzir operação inadequada.

### 8.2 Desenho mínimo

- coorte consentida e grupo de controle;
- uma ou duas classes de investimento;
- conjunto pequeno de sinais já aprovados;
- nenhuma ordem, recomendação ou catálogo de produtos;
- execução no ambiente da instituição;
- duração suficiente para observar mais de um evento relevante;
- textos e limiares aprovados antes da ativação.

### 8.3 Métricas de compra

| Pilar | Métrica inicial |
|---|---|
| Adoção | clientes elegíveis que abrem a explicação |
| Retenção | retorno ao canal em 7, 30 e 90 dias |
| Compreensão | conclusão da explicação e resposta curta de utilidade |
| Eficiência | tempo de atendimento ou assessoria por dúvida de mercado |
| Qualidade | alertas irrelevantes, opt-out, reclamação e correção manual |
| Negócio | revisão de carteira ou aporte, medido com grupo de controle e sem atribuir causalidade indevida |
| Risco | decisões sem recibo, falha de consentimento ou exposição indevida — meta zero |

Os limiares comerciais serão definidos com a instituição antes do piloto. Não
se deve declarar ROI com base apenas em abertura de tela ou correlação simples.

## 9. Roadmap aprovado

### Fase A — produto móvel confiável

- development build em aparelho real;
- carteira local editável e criptografada;
- importação B3 sanitizada;
- histórico local, favoritos e alertas explicáveis;
- E2E Android/iOS e gates de produção móvel.

### Fase B — fundação Embedded

- Intelligence API e contrato de recibo;
- sandbox inteiramente sintético;
- Exposure Adapter executado na fronteira privada;
- SDK white-label inicial;
- versionamento e compatibilidade contratual.

### Fase C — governança e piloto

- Governance Studio;
- RBAC, trilha de auditoria, replay e kill switch;
- observabilidade e telemetria minimizada;
- pacote de segurança, operação e continuidade;
- piloto controlado com posições internas da instituição.

### Fase D — expansão regulada

- autenticação e consentimento compatíveis com a arquitetura da instituição;
- avaliação de Open Finance e contas externas;
- Advisor Copilot;
- camada opcional de produtos, somente com suitability e governança aprovadas;
- escala multi-instituição depois de um piloto reproduzível.

A ordem detalhada, seus gates e o próximo incremento estão em
`docs/product/PLANO_FOCUSLENS.md`. A arquitetura-alvo está em
`docs/architecture/ARQUITETURA_INSTITUCIONAL.md`.

## 10. Guardrails permanentes

- não prometer previsão, retorno ou causalidade não demonstrada;
- não emitir compra, venda ou produto recomendado no motor educacional;
- não usar carteira real no snapshot público ou nos testes versionados;
- não enviar posição, valor ou identificador pessoal para telemetria;
- não duplicar fórmulas dos motores em SDK ou UI;
- não iniciar Open Finance antes dos gates de segurança e consentimento;
- não tratar esta estratégia como parecer regulatório;
- submeter integração regulada, suitability, LGPD e comunicação comercial à
  validação final jurídica e de compliance da instituição.

## 11. Referências externas de arquitetura e mercado

- Banco Central — escala e resultados do Open Finance em 2025:
  https://www.bcb.gov.br/detalhenoticia/20813/noticia
- Open Finance Brasil — Financial-grade API Security Profile:
  https://openfinancebrasil.atlassian.net/wiki/spaces/OF/pages/1334149137
- OWASP — uso combinado de MASVS, ASVS e threat modeling:
  https://mas.owasp.org/MASVS/03-Using_the_MASVS/
- Banco Central — Resolução CMN nº 4.893, segurança cibernética e contratação
  de processamento/armazenamento de dados:
  https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=4.893&tipo=Resolu%C3%A7%C3%A3o+CMN
