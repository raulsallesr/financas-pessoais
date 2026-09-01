# FocusLens BR — plano do produto

> Expectativas, preços e cenários do mercado brasileiro, com método e fontes
> visíveis.

Este é o documento canônico da evolução do projeto. Ele organiza o produto em
entregas pequenas e publicáveis, sem fragmentar o código em vários repositórios.
Cada etapa deve funcionar sozinha; juntas, elas formam o FocusLens BR.

## 1. Proposta

O FocusLens BR responde, em linguagem direta, a três perguntas:

1. O que mudou nas expectativas do Boletim Focus?
2. O que mudou nas taxas dos títulos públicos?
3. Focus e curva de juros estão contando histórias compatíveis?

O produto é educacional e analítico. Ele organiza dados públicos e explicita o
método utilizado, sem emitir recomendação personalizada de investimento.

## 2. Princípios

- **Uma resposta primeiro:** a tela começa pela principal mudança, não por uma
  coleção de gráficos.
- **Evidência perto da conclusão:** toda leitura mostra números, datas e fonte.
- **Precisão antes de sofisticação:** começamos por títulos prefixados sem cupom
  e pontos observados; modelos mais complexos entram somente quando necessários.
- **Camadas progressivas:** síntese aberta; tabela, metodologia e detalhes sob
  demanda.
- **Sem falsa certeza:** dado defasado, série incompatível ou sinal misto aparece
  como limite, não é preenchido por narrativa.
- **Sem recomendação:** não há ordem de compra, venda, promessa ou alvo de preço.
- **Um repositório, entregas independentes:** cada marco recebe versão, demo e
  publicação próprios, mas reaproveita a mesma arquitetura.

## 3. Público

Público principal:

- pessoas que trabalham ou estudam finanças, dados e economia;
- profissionais de tesouraria, risco, ALM e produtos financeiros;
- recrutadores e equipes técnicas avaliando capacidade de produto e engenharia.

O produto deve ser compreensível para uma pessoa interessada em mercado sem
exigir domínio de construção de curvas.

## 4. Jornada final

### Resumo

- principal mudança do período;
- estado das fontes e data de atualização;
- leitura Focus × curva quando houver evidência suficiente;
- acesso direto à explicação.

### Expectativas

- Selic, IPCA, PIB e câmbio;
- comparação com a leitura anterior;
- revisões mais relevantes;
- histórico e notícias como contexto rastreável.

### Curva e cenários

- taxas por vencimento;
- curva atual contra semana e mês anteriores;
- variação em pontos-base;
- cenários simples de choque, somente após o motor-base estar validado.

### Carteira

- permanece como módulo opcional e local;
- dados pessoais continuam apenas na sessão;
- nunca alimenta o motor educacional nem altera o veredito público.

O Radar Macro atual será preservado durante a evolução. Na integração final,
seus sinais úteis serão incorporados ao Resumo, evitando uma seção paralela que
repita o Focus ou a curva.

## 5. Roadmap de entregas

### Etapa 0 — Fundação do FocusLens BR

**Objetivo:** registrar a tese, os limites, o padrão visual e a sequência de
entregas.

**Entrega:** este plano, README alinhado e estado atualizado no `CONTEXT.md`.

**Estado:** concluída em 2026-08-26.

---

### Etapa 1 — Focus Semanal

**Pergunta:** o que realmente mudou no Focus desde a leitura anterior?

**Entra:**

- Selic, IPCA, PIB e câmbio;
- ranking das três revisões mais relevantes;
- comparação entre datas reais de coleta;
- estado `Atualizado`, `Defasado`, `Indisponível` ou `Sem mudança relevante`;
- histórico e dados completos sob demanda;
- captura visual e README preparados para publicação.

**Não entra:** curva de juros, modelo probabilístico, IA generativa ou nova fonte.

**Aceite:**

- uma pessoa entende a principal mudança em até dez segundos;
- toda conclusão exibe valor anterior, atual, intervalo e fonte;
- ausência de mudança ou de dado tem estado próprio;
- suíte atual e novos testes passam;
- a entrega recebe versão e material de publicação.

**Versão-alvo:** `v1.12`.

**Publicação:** “Criei um monitor automático para mostrar o que mudou no
Boletim Focus — sem depender do PDF.”

**Estado:** concluída em 2026-08-26. O motor puro normaliza cada delta pelo
limiar do indicador, a interface prioriza até três revisões e os quatro estados
de disponibilidade foram cobertos por testes. Método e captura estão em
`METODOLOGIA_FOCUS.md` e `docs/assets/focus-semanal-v1.12.png`.

---

### Etapa 2 — Curva Tesouro

**Pergunta:** como as taxas dos títulos prefixados mudaram?

**Entra:**

- fonte pública do Tesouro Transparente;
- inicialmente, títulos prefixados sem cupom;
- pontos observados por vencimento, sem inventar precisão entre eles;
- curva atual contra D-5 e D-21 úteis disponíveis;
- variação em pontos-base por título;
- tabela acessível e estado independente da fonte.

**Não entra:** NTN-F, IPCA+, crédito privado, DI futuro, ANBIMA obrigatória ou
recomendação de título.

**Aceite:**

- data, título, vencimento e taxa preservam rastreabilidade até a fonte;
- famílias de títulos incompatíveis não são misturadas;
- comparação usa datas efetivamente disponíveis;
- gráfico diferencia períodos por cor e estilo de linha;
- valores exatos também existem em tabela;
- falha do Tesouro não derruba Focus, Radar ou Carteira.

**Versão-alvo:** `v1.13`.

**Publicação:** “Transformei dados públicos do Tesouro em uma leitura direta da
curva prefixada brasileira.”

**Estado:** concluída em 2026-08-26. A implementação usa a taxa de compra da
manhã, filtra somente prefixados sem cupom, seleciona D-5/D-21 entre datas
publicadas e compara apenas vencimentos idênticos. O método está em
`METODOLOGIA_CURVA.md`; cache, automação, gráfico, tabela e estados da fonte
foram integrados sem nova dependência.

---

### Etapa 3 — Focus × Curva

**Pergunta:** expectativas declaradas e taxas de mercado se movem na mesma
direção?

**Entra:**

- motor determinístico e explicável de convergência;
- estados `Alinhados`, `Curva mais pressionada`, `Curva mais benigna`,
  `Sinais mistos` e `Dados insuficientes`;
- evidências numéricas e condições que mudariam a leitura;
- distinção entre ponta curta e longa quando a cobertura permitir.

**Limite metodológico obrigatório:** taxa de título público não é uma previsão
pura da Selic. O diferencial também pode refletir prêmio de prazo, risco e
liquidez; o produto nunca apresenta esse spread como causalidade comprovada.

**Aceite:**

- cada estado deriva de regra testada e documentada;
- nenhuma notícia altera o cálculo numérico;
- sinal ambíguo permanece ambíguo;
- o veredito sempre mostra “O que prova” e “O que faria mudar”.

**Versão-alvo:** `v1.14`.

**Publicação:** “O mercado está precificando a mesma história que declara no
Focus?”

**Estado:** concluída em 2026-08-26. O motor compara a revisão da Selic para a
mesma reunião com a mediana D-5 dos vencimentos em comum, preserva sinais
mistos entre as pontas e degrada para dados insuficientes sem completar
lacunas. Evidências, limiares e datas ficam junto do veredito; o método está em
`METODOLOGIA_FOCUS_CURVA.md`.

---

### Etapa 4 — FocusLens BR

**Objetivo:** consolidar as entregas anteriores em uma experiência única e
publicável.

**Entra:**

- Resumo, Expectativas, Curva e Carteira em uma hierarquia única;
- cenário simples de choques paralelos na curva;
- metodologia unificada;
- demo pública, documentação de arquitetura e histórico de versões;
- auditoria final de privacidade, segredos, licenças e fontes.

**Fica para depois do lançamento:** curva real de IPCA+, bootstrap com títulos
de cupom, forwards, backtest por regime e probabilidades calibradas.

**Versão-alvo:** `v2.0`.

**Estado:** release candidate concluído em 2026-08-27. A abertura pública e a
tag/release aguardam a decisão sobre licença do código e e-mail histórico.

---

### Etapa 5 — FocusLens Mobile

**Pergunta:** o que o mercado está dizendo agora e onde isso encosta nos
investimentos que a pessoa já possui?

**Objetivo:** transformar os motores do FocusLens em um app Android/iOS útil,
explorável e pessoal, com padrão de explicabilidade, privacidade e acabamento
compatível com um produto que também poderia integrar o ecossistema digital de
uma instituição financeira.

**Experiência-alvo:**

- Hoje: um veredito, sinais tocáveis, data, fonte e evidência;
- Carteira: exposição local, privacidade e filtro por classe/posição;
- Cenários: hipóteses mecânicas com resposta imediata e limites visíveis;
- Entenda: método curto, comparações e educação contextual;
- alertas futuros sempre explicam `o que mudou`, `o que prova`, `onde afeta` e
  `o que não prova`.

**Incrementos:**

1. **Fundação móvel `v0.1` — concluída em 2026-08-27.** React Native + Expo +
   TypeScript; quatro áreas, navegação persistente, carteira sintética,
   filtros, cenários, marca própria, testes de domínio e bundle Android.
2. **Contrato vivo.** Gerar snapshot JSON versionado a partir dos motores
   Python, validar compatibilidade e substituir o provider demo por leitura com
   cache/fallback, sem duplicar regras financeiras no app.
3. **Carteira realmente pessoal.** Editor local, ocultação de valores,
   armazenamento criptografado e importação B3 sanitizada; nenhuma nuvem por
   padrão.
4. **Acompanhamento divertido e útil.** Favoritos, comparação entre
   fotografias, alertas explicáveis, simulador de aportes e trilhas educativas,
   sem gamificação que incentive giro ou risco.
5. **Prontidão institucional.** Autenticação, consentimento, threat model,
   observabilidade sem dado financeiro, acessibilidade E2E, assinatura de
   builds e, somente depois, avaliação de Open Finance e integração bancária.

**Não entra nesta fundação:** ordem de compra/venda, recomendação personalizada,
sincronização de conta, Open Finance, cloud de carteira ou publicação em loja.

**Aceite da fundação móvel:**

- Android e iOS compartilham a mesma base React Native;
- toque em um sinal filtra somente posições relacionadas;
- valores pessoais podem ser ocultados e a demo é explicitamente sintética;
- cenário de mercado não calcula preço, retorno ou probabilidade; o laboratório
  usa apenas taxa fixa digitada e rotulada como hipótese matemática;
- alvos interativos têm no mínimo 44 px, navegação funciona com rótulos e o
  layout passa em celular pequeno, celular grande, tablet e paisagem;
- TypeScript, testes de domínio e export Android passam.

**Estado:** fundação `v0.1`, contrato vivo `v1`, distribuição Android, carteira
local, importação B3 e os três primeiros incrementos da Etapa 5C chegaram ao
preview `v0.5.2/11`. O Raul confirmou a instalação desse APK em 2026-08-31;
gates físicos permanecem parciais e pausados. A revisão guiada da semana
`v0.5.3` e o laboratório educacional `v0.5.4`–`v0.6.4` foram concluídos
localmente e estão documentados nas seções 24 a 35. O corte atual organiza
Cenários por intenção e inclui aportes variáveis, parcelamento e duração de um
saldo sob retiradas mensais.

## 6. Arquitetura

A separação atual continua valendo: motor puro, adaptador de I/O e UI nunca
devem virar uma única camada.

Módulos previstos, criados somente quando a etapa correspondente começar:

```text
curva_data.py             modelos e transformações puras
curva_fontes.py           coleta do Tesouro Transparente
curva_modelo.py           pontos, inclinação e variação em bps
curva_cenarios.py         choques simples e sensibilidade
convergencia_modelo.py    regras Focus × curva
pagina_curva.py           apresentação Streamlit
atualizar_curva_cache.py  automação sem Streamlit
METODOLOGIA_CURVA.md      fórmulas, fontes e limitações
```

A partir da Etapa 5, `mobile/` adiciona uma camada consumidora sem substituir
os motores:

```text
mobile/src/data/          provider demo; depois snapshot vivo versionado
mobile/src/domain/        contrato, filtros e sensibilidade educacional
mobile/src/components/    componentes React Native acessíveis
mobile/src/screens/       Hoje, Carteira, Cenários e Entenda
mobile/tests/             gate do domínio TypeScript
```

A fronteira detalhada está em `docs/ARQUITETURA_MOBILE.md`.

Pastas vazias e abstrações antecipadas não serão criadas. Cada módulo nasce com
uso real e teste correspondente.

## 7. Contratos mínimos de dados

### Fotografia Focus

```text
indicador, referencia, data_coleta, mediana, media,
minimo, maximo, desvio_padrao, num_respondentes
```

### Ponto da curva

```text
data_referencia, tipo_titulo, vencimento, taxa_compra,
taxa_venda, pu_compra, pu_venda, fonte
```

### Leitura Focus × curva

```text
estado, titulo, resumo, evidencias, ressalvas,
condicoes_de_mudanca, datas_das_fontes
```

O contrato da fonte deve refletir os campos realmente disponíveis. Campo
ausente não recebe zero nem valor inventado.

## 8. Direção visual

O FocusLens BR evolui a identidade já aprovada; não adota uma aparência nova a
cada etapa.

### Personalidade

- editorial financeiro;
- clara, sóbria e contemporânea;
- densa o suficiente para decidir, sem parecer terminal de trading;
- poucos elementos decorativos.

### Tokens preservados

- fundo: verde-neutro muito claro `#F3F7F5`;
- superfície: branco `#FFFFFF`;
- texto: verde profundo `#17332F`;
- primária: verde-petróleo `#0F766E`;
- destaque: dourado discreto `#A16207`;
- borda: `#D8E5E1`.

Não será adicionada fonte externa apenas por estética. A tipografia do sistema,
os números tabulares e os tokens centralizados existentes são suficientes.

### Hierarquia

1. um veredito ou principal mudança;
2. duas a quatro métricas que sustentam a leitura;
3. gráfico principal;
4. explicação e riscos;
5. tabela e metodologia recolhidas.

### Gráficos

- linha para evolução temporal e curva por vencimento;
- período atual em linha sólida; comparação em tracejado;
- no máximo quatro séries simultâneas;
- pontos relevantes recebem marcador e rótulo, não apenas cor;
- valores exatos sempre disponíveis em tabela;
- sem velocímetros, 3D, roscas decorativas ou animação gratuita.

### Responsividade e acessibilidade

- conteúdo limitado a aproximadamente 1100 px;
- alvos interativos mínimos de 44 px;
- contraste WCAG AA;
- foco de teclado visível;
- nenhum significado transmitido somente por cor;
- validação em 375, 768, 1024 e 1440 px;
- movimento reduzido respeitado.

## 9. Definição de pronto por etapa

Uma etapa só pode ser chamada de publicável quando cumprir os quatro gates:

### Produto

- responde à pergunta da etapa sem depender da próxima;
- possui estados de dado atualizado, defasado, vazio e indisponível;
- não contém promessa ou recomendação financeira.

### Engenharia

- motor puro separado do I/O e da UI;
- testes de unidade, integração sintética e `AppTest` quando houver tela;
- suíte completa, `py_compile` e `git diff --check` limpos;
- sem segredo, dado pessoal ou arquivo real de carteira.

### Visual

- conclusão compreensível antes dos detalhes;
- números, datas e fontes visíveis;
- desktop e mobile sem sobreposição ou rolagem horizontal;
- tabela alternativa para gráfico.

### Publicação

- README atualizado;
- metodologia e limitações documentadas;
- uma captura principal e uma imagem técnica;
- tag/release no GitHub;
- post curto no LinkedIn com problema, solução, aprendizado e link.

## 10. Estratégia de publicação

Os marcos serão tratados como pequenos produtos, não como repositórios
descartáveis:

| Marco | História pública | Versão |
|---|---|---|
| Focus Semanal | O que mudou nas expectativas | `v1.12` |
| Curva Tesouro | O que mudou nas taxas | `v1.13` |
| Focus × Curva | Expectativa versus precificação | `v1.14` |
| FocusLens BR | Produto integrado | `v2.0` |

Antes de tornar o repositório público, executar auditoria específica de
segredos, dados pessoais, direitos de conteúdo, dependências e histórico Git.

## 11. Execução da Etapa 4 — concluída tecnicamente

As Etapas 1, 2 e 3 estão fechadas nas versões `v1.12`, `v1.13` e `v1.14`.
A execução consolidou o FocusLens BR `v2.0` sem recalcular, dentro da UI, o que
os motores já entregam.

### Ordem de implementação

1. **Fechar o contrato do Resumo integrado — concluído em 2026-08-27.** A
   camada pura `resumo_integrado.py` consome `ResumoFocusSemanal`,
   `LeituraCurva` e `LeituraConvergencia` e devolve uma prioridade, um
   veredito, duas a quatro provas e as datas das
   fontes. Ela deve apenas orquestrar os resultados existentes; fórmulas de
   Focus, curva e convergência continuam em seus motores de origem. A regra
   implementada prioriza convergência íntegra, revisão relevante do Focus,
   curva atual, Focus atual e, por último, qualidade dos dados; limites e
   condições de mudança também permanecem no contrato.
2. **Consolidar a hierarquia da página única — concluído em 2026-08-27.** A
   jornada final agora segue Resumo → Expectativas → Curva → Carteira. O
   Resumo consome o contrato puro na primeira dobra e seleciona no máximo um
   sinal externo do Radar, excluindo sinais que repetiriam o Focus. A carga
   completa do Radar foi preservada para a Carteira e sua apresentação antiga
   continua coberta por teste, sem permanecer como seção paralela da Home.
3. **Adicionar o cenário de curva — concluído em 2026-08-27.**
   `curva_cenarios.py` recebe a fotografia atual e um choque explícito em bps,
   desloca todos os pontos sem mutar a base e devolve taxas, inclinações,
   narrativa e limites. A UI compara Observada × Cenário entre −100 e +100
   bps; não estima probabilidade, retorno de carteira, preço-alvo nem
   recomendação e não abre escopo para bootstrap, forwards, cupom ou IPCA+.
4. **Unificar metodologia e narrativa — concluído em 2026-08-27.**
   `METODOLOGIA_FOCUSLENS.md` conecta os contratos especializados e documenta
   prioridade, evidências, janelas, fontes, cenário e limites causais. O
   Resumo expõe a lógica sob demanda, sem repetir métricas nem recalcular os
   motores na UI.
5. **Fechar a publicação — concluído como release candidate em 2026-08-27.**
   README, histórico, release notes e texto de LinkedIn foram alinhados; a
   captura principal e o diagrama técnico foram gerados; privacidade, segredos,
   fontes, licenças, dependências e histórico Git foram auditados. A visibilidade
   não foi alterada: licença do código e e-mail histórico exigem decisão do
   titular antes da tag/release pública.

### Critérios de aceite específicos da integração

- A primeira dobra responde “o que merece atenção agora?” sem exigir que a
  pessoa percorra as seções anteriores.
- Cada fato possui um lugar canônico; nenhuma métrica aparece repetida apenas
  para preencher cards.
- O veredito sempre mantém prova numérica, datas, fonte, limite e condição de
  mudança próximos da ação de leitura.
- Falha de uma fonte degrada somente a parte dependente dela e não inventa uma
  síntese com dados ausentes.
- A composição continua utilizável em 375, 768, 1024 e 1440 px, sem rolagem
  horizontal e sem significado transmitido apenas por cor.
- A suíte inteira, `py_compile`, `pip check` e `git diff --check` passam.

### Gate local de engenharia

No PowerShell, dentro do projeto e com o ambiente externo já criado:

```powershell
$pythonProjeto = "$env:USERPROFILE\.venvs\financas-pessoais\Scripts\python.exe"
$baseTemporaria = Join-Path $env:TEMP ("fp_pytest_" + [guid]::NewGuid().ToString("N"))
$arquivosPython = @(git ls-files "*.py")
& $pythonProjeto -m pytest tests -q --basetemp $baseTemporaria -p no:cacheprovider
& $pythonProjeto -m py_compile $arquivosPython
& $pythonProjeto -m pip check
git diff --check
```

No Windows/OneDrive, `WinError 5` em diretórios temporários pode ser ruído do
sandbox nos testes de cache atômico. Se ocorrer, não afrouxar a implementação:
repetir a suíte fora do sandbox, com um `--basetemp` único, e registrar os dois
resultados.

## 12. Execução da Etapa 5, incremento 2 — concluída

### Resultado esperado

Conectar o primeiro dado vivo ao app sem transformar a interface em um segundo
motor financeiro. Ao final, o app lê uma fotografia pública, versionada e
gerada pelos contratos Python já aprovados; se ela estiver ausente ou inválida,
continua navegável com a demo e identifica claramente o fallback.

Esta entrega não inclui APK/AAB, conta real, nuvem, Open Finance, importação B3
ou armazenamento de carteira. Esses itens continuam em incrementos separados.

**Estado:** concluída em 2026-08-27. `mobile_snapshot.py` consome os quatro
contratos aprovados, `gerar_mobile_snapshot.py` grava o JSON público de forma
atômica e `snapshotProvider.ts` seleciona live ou demo sem espalhar condicionais
pelas telas. Nenhum motor `v1.12`–`v2.0` foi alterado.

### Checklist de implementação

1. **Fechar o contrato antes da UI.** Definir a versão `1` do snapshot com, no
   mínimo: `schemaVersion`, `mode`, `generatedAt`, `asOf`, veredito e suporte,
   disponibilidade das fontes e sinais com identificador, valor apresentado,
   movimento, explicação, fonte, data, tom e efeitos por classe. Datas devem ser
   serializadas em ISO; a formatação humana continua na apresentação.
2. **Separar mercado de carteira.** O artefato gerado pelo Python não pode
   conter `positions`, `amount`, patrimônio ou identificador pessoal. A carteira
   demo permanece uma fixture local do app; uma carteira real só entra no
   incremento de armazenamento local criptografado.
3. **Serializar contratos, não recalcular.** Criar um adaptador Python que
   consuma `ResumoIntegrado`, `ResumoFocusSemanal`, `LeituraCurva` e
   `LeituraConvergencia`. Reutilizar os formatadores/apresentadores existentes
   quando necessário; não duplicar mediana, D-5/D-21, relevância ou regras de
   convergência.
4. **Gerar um JSON determinístico.** Escrever em arquivo temporário e substituir
   o destino de forma atômica, com UTF-8, ordenação estável e newline final. A
   geração usa somente os caches públicos versionados e não consulta rede. O
   artefato deve ser pequeno, revisável no diff e seguro para versionamento.
5. **Validar na borda móvel.** Ampliar o contrato TypeScript para `demo | live`
   e validar a estrutura antes de usá-la. Um schema desconhecido, campo
   obrigatório ausente ou JSON inválido deve selecionar a demo, sem exceção não
   tratada.
6. **Criar o provider read-only.** Centralizar a escolha live → fallback demo em
   `mobile/src/data/`, sem espalhar condicionais pelas telas. O provider combina
   o mercado público com a carteira demo local apenas em memória.
7. **Tornar a origem visível.** Hoje deve indicar “Dados públicos” ou
   “Demonstração”, data da fotografia e fontes disponíveis. O fallback não pode
   parecer dado atual. Carteira, Cenários e Entenda continuam funcionando com
   quantidade variável de sinais.
8. **Cobrir falhas e compatibilidade.** Adicionar testes Python para schema,
   determinismo, ausência de dados pessoais e degradação por fonte; adicionar
   testes móveis para snapshot válido, versão incompatível, documento inválido,
   fallback demo e preservação dos filtros por classe.
9. **Validar o produto completo.** Rodar os gates Python e móvel, abrir a prévia
   e conferir 375×812, 430×932, 768×1024 e 844×390. Verificar overflow,
   truncamento, alvos de toque, contraste, foco e entendimento sem depender de
   cor. Registrar nova captura somente se houver mudança visual material.
10. **Fechar o incremento.** Atualizar `README.md`, `mobile/README.md`,
    `docs/ARQUITETURA_MOBILE.md`, este plano e `CONTEXT.md`; conferir
    `git diff --check`; commitar e publicar apenas no remote próprio do projeto.

### Critérios de aceite

- O snapshot vivo nasce dos motores Python e possui versão explícita.
- Nenhum cálculo financeiro aprovado foi reimplementado em TypeScript.
- Nenhuma posição ou quantia pessoal sai no artefato público.
- Falha ou incompatibilidade ativa uma demo claramente rotulada.
- A navegação e os impactos continuam íntegros com dados live e demo.
- Suíte Python, `py_compile`, `pip check`, TypeScript, testes de domínio, export
  Android e `git diff --check` passam.
- O layout permanece utilizável nos quatro viewports definidos, sem overflow
  horizontal e sem informação transmitida apenas por cor.

### Fora de escopo e ordem posterior

Depois deste contrato: development build instalável; carteira local editável e
criptografada; importação B3 sanitizada; alertas/favoritos; E2E em Android/iOS;
e somente então autenticação e avaliação de Open Finance. Não antecipar essas
frentes dentro do incremento 2.

### Evidência de fechamento

- O artefato versionado `mobile/src/data/liveSnapshot.json` contém schema `1`,
  datas ISO, veredito, provas, fontes, limites e quatro sinais; não contém
  posição, quantia ou identificador pessoal.
- Geração repetida com os mesmos contratos preserva `generatedAt` e produz os
  mesmos bytes; a escrita usa arquivo temporário, `fsync` e `os.replace`.
- Schema incompatível, JSON inválido, campo obrigatório ausente ou chave de
  carteira ativam a demo sintética com motivo visível; a navegação não cai.
- Gate: 191 testes Python e 10 testes móveis; `py_compile`, `pip check`,
  TypeScript, export Android e `git diff --check` aprovados.
- Validação visual real em 375×812, 430×932, 768×1024 e 844×390 confirmou
  `scrollWidth == clientWidth`, origem textual, data/fonte e navegação sem
  depender apenas de cor.

## 13. Execução da Etapa 5A — build de desenvolvimento

### Resultado esperado

Instalar o app em um aparelho Android por um development build próprio, sem
alterar o contrato público nem antecipar carteira real. Registrar a rota
equivalente para iOS, que depende de ambiente e assinatura Apple compatíveis.

### Escopo fechado

1. configurar o projeto EAS/development client sem versionar credencial ou
   segredo;
2. gerar um build Android instalável de desenvolvimento e validar as quatro
   abas em aparelho real;
3. confirmar carregamento do snapshot empacotado e fallback demo offline;
4. testar safe areas, gesto voltar, rotação, leitor de tela e tamanho de fonte;
5. documentar comandos, requisitos, artefatos ignorados e limites do build;
6. manter carteira editável, importação B3, alertas, autenticação e Open
   Finance fora deste incremento.

### Estado da execução em 2026-08-28

**Em andamento; fechamento de acessibilidade pendente.** A configuração portátil do build está
fechada: Expo SDK `57.0.18`, `expo-dev-client`, EAS CLI mínimo `23.0.0`, perfis
`development`/`preview`, identificadores nativos, scheme, safe areas, rotação e
splash compatível. Expo Doctor passou `21/21`, TypeScript e os testes móveis
passaram e o bundle Android/Hermes foi exportado.

O login foi concluído localmente como `raulsallesr`, sem registrar credencial no
repositório. `eas init` criou `@raulsallesr/focuslens-br` e vinculou o
`projectId` público. Os dois builds Android associados ao commit `60fa378` e ao
mesmo fingerprint foram concluídos:

- `development`: `1ca28edc-ee9f-4b21-8ec6-6ba8baa9b918`;
- `preview`: `dd050dbe-5d0d-44e8-aae8-e13f613b7405`.

DB-01 a DB-05 e DB-07 a DB-09 estão aprovados no POCO X8 Pro; DB-06 permanece coberto pelos
testes automatizados. O development build foi instalado, mas a conexão LAN com
o Metro foi bloqueada pelo firewall corporativo `BlockInbound`; o preview foi
instalado em seguida e aprovou quatro abas, snapshot e reabertura em modo avião.
O aparelho usa Android 16 (`BP2A.250605.031.A3`).

Completar DB-10 a DB-12 em `docs/VALIDACAO_DEVELOPMENT_BUILD.md`: TalkBack,
texto ampliado e alvos de toque. Esses gates foram pausados por decisão do Raul
enquanto a utilidade cotidiana do produto é refinada no `v0.4.4`.
Não marcar esta seção como concluída só porque o fluxo principal e o offline
passaram; a evidência de acessibilidade continua obrigatória.

## 14. Roadmap aprovado — FocusLens Embedded

**Decisão de 2026-08-27:** o produto pessoal continuará evoluindo como app
móvel e cliente de referência. Sobre os mesmos motores e contratos será criada,
somente depois dos gates móveis, uma camada institucional incorporável chamada
**FocusLens Embedded**.

A tese, o pacote comercial e o desenho do piloto estão em
`docs/ESTRATEGIA_INSTITUCIONAL.md`. Fronteiras, contratos, segurança,
observabilidade e gates estão em `docs/ARQUITETURA_INSTITUCIONAL.md`.

### Sequência canônica

1. **Etapa 5A — distribuição móvel.** Concluir exatamente a seção 13:
   development build Android instalado e validado; rota iOS documentada.
2. **Etapa 5B — carteira pessoal segura.** Editor local, ocultação de valores,
   armazenamento criptografado e importação B3 sanitizada, sem nuvem por
   padrão. Editor, cofre privado `v1` e importação B3 com prévia estão
   implementados no corte móvel `v0.4`; a validação física permanece no gate.
3. **Etapa 5C — acompanhamento explicável.** Histórico local de fotografias,
   favoritos, alertas com evidência, simulador de aportes, testes de componentes
   e E2E Android/iOS.
4. **Etapa 6 — fundação Embedded.** Intelligence API, receipt versionado,
   sandbox sintético, Exposure Adapter privado e primeiro SDK white-label.
5. **Etapa 7 — governança e piloto.** Governance Studio, RBAC, auditoria,
   replay, kill switch, observabilidade, continuidade e piloto controlado com
   dados que a própria instituição já mantém.
6. **Etapa 8 — expansão regulada.** Avaliar autenticação, Open Finance, contas
   externas e Advisor Copilot depois que o piloto comprovar valor e os gates de
   segurança, jurídico, compliance e risco forem aprovados.

### Primeiro caso de uso institucional

> Algo relevante mudou no mercado. Estas partes da carteira consentida são
> sensíveis a isso. Veja o que prova a relação, quais são os limites e qual
> versão da regra produziu a explicação.

Cada decisão deverá produzir um receipt reproduzível com sinal, fonte, data,
evidência, regra, versão, exposição relacionada, limite e política de entrega.
O snapshot móvel público `v1` continuará sem posição, valor ou identificador.

### Gates para iniciar a Etapa 6

- development build e carteira local segura concluídos;
- experiência de alertas explicáveis validada sem recomendação ou ordem;
- testes de componentes e E2E móvel aprovados;
- licença do código e cadeia de titularidade resolvidas;
- contrato de receipt fechado com exemplos exclusivamente sintéticos;
- threat model inicial e fronteiras de dados revisados;
- nenhum dado de carteira no plano público ou em telemetria;
- decisão explícita do Raul para iniciar o sandbox institucional.

### Gates para iniciar um piloto

- API e SDK com compatibilidade versionada;
- ambiente privado da instituição e contexto de exposição minimizado;
- identidade, consentimento, revogação e RBAC integrados;
- Governance Studio com aprovação, replay e kill switch;
- logs e métricas sem posição ou valor financeiro bruto;
- segurança, privacidade, continuidade e incidentes documentados;
- coorte, controle, métricas de compra e limiares comerciais acordados;
- avaliações finais das áreas jurídica, compliance, segurança e risco da
  instituição.

### Guardrails da trilha institucional

- Open Finance não é dependência do primeiro piloto;
- os motores não recebem identidade, consentimento ou catálogo de produtos;
- a carteira entra somente dentro da fronteira privada da instituição;
- SDK e UI não reimplementam fórmula financeira;
- explicação educacional e recomendação comercial permanecem camadas distintas;
- IA generativa futura poderá resumir evidências aprovadas, nunca criar o
  veredito ou contornar a política institucional;
- esta arquitetura é proposta técnica, não parecer regulatório.

## 15. Execução da Etapa 5B, incremento 1 — carteira local segura

### Resultado esperado

Permitir que a pessoa substitua conscientemente a carteira fictícia por posições
próprias, sem conta, backend ou nuvem e sem ampliar o snapshot público `v1`.

### Escopo fechado

1. criar, editar e excluir posições locais com nome, classe e valor;
2. manter o controle de ocultação e conectar as posições locais às mesmas
   leituras educacionais já existentes;
3. guardar somente a chave criptográfica no cofre nativo do sistema;
4. guardar o documento privado `v1` como arquivo AES-256-GCM autenticado, com
   gravação temporária seguida de substituição atômica;
5. falhar fechado se chave, autenticação ou contrato forem inválidos, oferecendo
   reset explícito sem misturar a carteira demo;
6. manter a bancada web em demonstração e o editor seguro somente nos apps
   Android/iOS;
7. deixar importação B3, biometria, sincronização, autenticação e Open Finance
   fora deste incremento.

### Estado da execução em 2026-08-28

**Implementação e gates locais concluídos; ciclo funcional aprovado.** O
corte móvel foi elevado a `v0.3.0`. `expo-crypto`, `expo-file-system` e
`expo-secure-store` estão nas versões recomendadas para o Expo 57. O contrato
privado aceita até 100 posições, valida identificadores, classes, nomes e valores
e permanece separado do snapshot público versionado.

A interface usa labels visíveis, teclado decimal, validação junto ao campo,
feedback de salvamento, confirmação destrutiva, estados indisponível/corrompido
e alvos mínimos de 48 px. A inspeção visual do formulário e do estado de
demonstração foi aprovada em renderer web; o web não persiste carteira.

Os gates locais aprovaram TypeScript, 20 testes de domínio, export web e bundle
Android/Hermes com 633 módulos. A primeira tentativa do Hermes dentro do sandbox
falhou com `spawn EPERM`; a repetição fora dele passou sem mudança de código.
O preview EAS `67b97c57-ce20-4cb6-8c21-570c4742762e`, associado ao commit
`9308f02` e fingerprint `a28c993ae571b5d58d7eea95f8fe6fc877c71023`,
terminou com status `FINISHED`. O ciclo foi executado no preview `v0.4.0` no
POCO X8 Pro: CL-02 a CL-10 foram aprovados; CL-11 a CL-13 permanecem pendentes
e pausados.
O roteiro e a matriz de evidência estão em
`docs/VALIDACAO_CARTEIRA_LOCAL.md`.

## 16. Execução da Etapa 5B, incremento 2 — importação B3 sanitizada

### Resultado esperado

Permitir que a pessoa escolha no Android/iOS a planilha XLSX da Área do
Investidor B3, revise uma versão mínima da posição e substitua conscientemente
a carteira local, sem backend, upload, persistência do original ou ampliação do
snapshot público `v1`.

### Escopo fechado

1. usar o seletor nativo com cópia temporária no cache privado e limite de 5 MB;
2. processar ZIP/XML somente em memória e apagar a cópia temporária em qualquer
   saída, sem alterar o arquivo original;
3. reconhecer apenas as abas B3 já cobertas pelo adaptador Python e extrair
   somente ativo, classe e valor atualizado;
4. consolidar linhas repetidas, ignorar subtotais e expor contagens de linhas
   aceitas, ignoradas e de classes não suportadas;
5. mostrar prévia com quantidade, total, abas e posições antes de qualquer
   gravação;
6. substituir a carteira inteira somente depois de confirmação explícita e
   cifrar o mesmo contrato privado `v1` no cofre existente;
7. manter web em demonstração e deixar CSV, PDF, nuvem, autenticação, Open
   Finance e novas classes de ativos fora deste incremento.

### Guardrails de arquivo

- rejeitar arquivo vazio, acima de 5 MB, não ZIP, macro-enabled ou sem a
  declaração XLSX esperada;
- extrair apenas manifestos, workbook, relações, shared strings e worksheets;
- limitar tamanho expandido, quantidade de entradas, XML individual, strings,
  linhas, células, posições e valor por posição;
- recusar DTD/entidades XML e relacionamento que saia de `xl/worksheets/`;
- não usar a biblioteca `xlsx` legada do npm; o leitor mínimo usa `fflate`
  somente para descompressão e interpreta o subconjunto OOXML necessário;
- não registrar nome de ativo, valor, nome de arquivo ou conteúdo em log,
  telemetria, EAS, snapshot ou documentação.

### Estado da execução em 2026-08-28

**Implementação, gates locais e preview concluídos; validação física
parcial.** O app foi elevado a `v0.4.0`, Android `versionCode 4` e iOS
`buildNumber 4`. `expo-document-picker ~57.0.1` e `fflate 0.8.3` foram
adicionados sem alterar motores Python ou o contrato público.

O fluxo usa labels e estados acessíveis, botão bloqueado durante leitura/gravação,
prévia progressiva, aviso explícito para classes excluídas e confirmação antes
de substituir a carteira. A importação nunca soma com posições antigas sem que
a pessoa perceba.

TypeScript, 25 testes de domínio, export web, `expo install --check`, Expo
Doctor `21/21` e bundle Android/Hermes com 640 módulos passaram. A auditoria de
dependências de produção encontrou zero vulnerabilidade; a árvore completa
mantém 11 moderadas transitivas do toolchain Expo, sem alta ou crítica. O
roteiro físico está em `docs/VALIDACAO_IMPORTACAO_B3.md`.

O preview EAS
[`c7695638-2f38-42a4-af07-92303f2a5ce0`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c7695638-2f38-42a4-af07-92303f2a5ce0)
terminou `FINISHED` para o commit `c6bb875`, fingerprint
`4df3790bd18465bb8a429b23f9814aabf1ac6dc8`, app `0.4.0` e build `4`. O
[APK interno](https://expo.dev/artifacts/eas/25BWk8wQe0mppgR7jumlP4VdI99WJctpNg_Nwjf5Cec.apk)
expira em 2026-09-11. No Android 16 (`BP2A.250605.031.A3`), BI-01 a BI-03
foram aprovados. BI-04 a BI-13 permanecem pendentes e pausados.

## 17. Refinamento de utilidade dentro da Etapa 5B — `v0.4.1`

### Decisão de produto em 2026-08-28

Depois de aprovar o ciclo funcional do cofre e o início do importador, o Raul
interrompeu os checklists restantes: o app ainda parecia uma demonstração e não
despertava vontade de uso. A prioridade passa temporariamente de validar mais
casos para tornar o valor cotidiano visível. Isso não fecha os gates físicos e
não antecipa a Etapa 5C.

### Escopo fechado

1. começar a Home pelo recorte da carteira, com posições, classes e maior
   concentração;
2. mostrar a cobertura que os sinais realmente possuem, declarando ausência de
   relação quando `effects` vier vazio;
3. resumir distribuição por classe antes da lista de posições;
4. manter sinais e posições longas sob revelação progressiva, sem carrossel
   horizontal como interação principal;
5. distinguir carteira local, demonstração, carregamento e cofre bloqueado em
   todas as telas que usam posições;
6. preservar a identidade visual clara já aprovada e os alvos mínimos de 48 px.

### Fora de escopo

- alterar qualquer motor Python ou fórmula financeira;
- ampliar ou reinterpretar o snapshot público `v1`;
- mudar cofre, persistência, importador B3 ou dependências nativas;
- implementar histórico, favoritos, alertas, E2E ou outro item da Etapa 5C;
- iniciar autenticação, Open Finance ou FocusLens Embedded.

### Estado da execução

**Implementado localmente.** O app foi elevado a `v0.4.1`, Android
`versionCode 5` e iOS `buildNumber 5`. A camada de apresentação ganhou resumo
por classe e cobertura de sinais calculados somente a partir dos contratos já
carregados. TypeScript, 27 testes móveis e export Android/Hermes com 640 módulos
passaram. O corte foi absorvido pelo `v0.4.2` antes de gerar preview; a avaliação
de utilidade continua na seção 18. BI-04 a BI-13, CL-11 a CL-13 e DB-10 a DB-12
continuam explicitamente pendentes.

## 18. Continuação do refinamento de utilidade — `v0.4.2`

### Resultado esperado

Fazer Cenários responder primeiro “qual parte da carteira muda de leitura?” e
permitir consultar o app em público sem o reaparecimento de valores ao trocar
de aba, ainda sem persistência nova ou regra de recomendação.

### Escopo fechado

1. elevar “Ocultar valores” para estado único da sessão;
2. aplicar a máscara existente em Hoje, Carteira e Cenários;
3. abrir Cenários em uma hipótese visível de +50 bps, mantendo a fotografia
   observada e os cinco controles disponíveis;
4. agregar impactos já produzidos por tom, quantidade de posições e percentual
   da carteira;
5. declarar o percentual sem relação mapeada em vez de aproximá-lo;
6. mostrar quatro posições inicialmente e expandir a lista sob demanda.

### Fora de escopo

- persistir a preferência de ocultação ou qualquer estado de cenário;
- mudar a matriz educacional, motores Python ou snapshot público `v1`;
- calcular retorno, preço, probabilidade, recomendação ou rebalanceamento;
- implementar histórico, alertas, favoritos, E2E, autenticação ou Embedded.

### Estado da execução

**Implementado localmente.** O app foi elevado a `v0.4.2`, Android
`versionCode 6` e iOS `buildNumber 6`. TypeScript, 29 testes móveis e o export
Android/Hermes com 640 módulos passaram. A Home e Cenários foram verificados em
375×812, 430×932, 768×1024 e 844×390 com `scrollWidth` igual à viewport. O modo
discreto permaneceu ativo entre Cenários e Carteira. O preview EAS ainda não foi
gerado; os gates físicos anteriores continuam pausados e não foram marcados
como aprovados.

## 19. Home em 10 segundos — `v0.4.3`

### Resultado esperado

Fazer a primeira dobra responder “como minha carteira está distribuída e o que
posso explorar agora?” antes de apresentar o mercado, sem revelar montantes nem
transformar concentração em recomendação.

### Escopo fechado

1. renderizar o recorte da carteira antes do contexto público de mercado;
2. mostrar maior classe, maior posição e cobertura atual como fatos percentuais;
3. usar uma única ação principal contextual: montar carteira na demonstração ou
   abrir a sensibilidade quando a carteira local já existe;
4. manter o mercado como contexto secundário, sob o título “Mercado em uma frase”;
5. ocultar o CTA redundante de Cenários quando a ação principal já leva à mesma aba.

### Fora de escopo

- sugerir compra, venda, rebalanceamento ou concentração desejável;
- alterar motores Python, matriz educacional ou snapshot público `v1`;
- mudar cofre, importação, persistência, dependências ou telemetria;
- gerar preview EAS ou retomar os gates físicos sem decisão explícita do Raul;
- antecipar histórico, alertas, E2E, autenticação ou Embedded.

### Estado da execução

**Implementado localmente.** O app foi elevado a `v0.4.3`, Android
`versionCode 7` e iOS `buildNumber 7`. TypeScript, 30 testes móveis e o export
Android/Hermes com 640 módulos passaram. A hierarquia, os três fatos, a ação
principal e `scrollWidth` igual à viewport foram confirmados em 375×812,
430×932, 768×1024 e 844×390. O preview EAS não foi gerado; BI-04 a BI-13,
CL-11 a CL-13 e DB-10 a DB-12 continuam pausados e pendentes.

## 20. Sua carteira em 1 minuto — `v0.4.4`

### Resultado esperado

Fazer a transição da demonstração para uma carteira local começar por uma ação
útil, curta e reversível, antes de pedir que a pessoa percorra toda a carteira
fictícia.

### Escopo fechado

1. colocar a entrada pessoal antes do patrimônio fictício no modo demonstração;
2. apresentar a importação B3 como caminho principal para preencher várias
   posições de uma vez;
3. manter a criação manual como alternativa visível e secundária;
4. preservar “Adicionar posição” como ação principal quando a carteira já é
   local;
5. manter prévia, confirmação e feedback do importador existentes.

### Fora de escopo

- mudar o parser XLSX, classes suportadas ou limites de arquivo;
- mudar cofre, contrato privado, persistência ou dependências;
- alterar motores Python ou snapshot público `v1`;
- criar onboarding persistido, telemetria, conta ou nuvem;
- gerar preview EAS, retomar gates físicos ou antecipar Etapa 5C/Embedded.

### Estado da execução

**Implementado e empacotado em 2026-08-31.** O app foi elevado a `v0.4.4`,
Android `versionCode 8` e iOS `buildNumber 8`. TypeScript e 30 testes móveis
passaram; o export Android/Hermes concluiu 640 módulos. A hierarquia da entrada,
os dois caminhos, os alvos de 52 px e
`scrollWidth` igual à viewport foram confirmados em 375×812, 430×932,
768×1024 e 844×390. O preview EAS interno
[`6199d700-82ca-44df-8ede-6987679c2566`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/6199d700-82ca-44df-8ede-6987679c2566)
terminou `FINISHED` no commit `565b071`, build `8`, fingerprint
`60a05723598a9a039fc90320bcf2a45eb945acaf`, sem variáveis `Plain text` ou
`Sensitive`. O APK expira em 2026-09-14; instalação e avaliação física deste
corte ainda estão pendentes. BI-04 a BI-13, CL-11 a CL-13 e DB-10 a DB-12
permanecem pausados e pendentes.

## 21. Etapa 5C, incremento 1 — acompanhamento explicável `v0.5.0`

### Decisão de produto em 2026-08-31

O Raul autorizou explicitamente iniciar a Etapa 5C para continuar aumentando a
vontade de uso. Essa decisão libera o desenvolvimento local da 5C, mas não
aprova nem remove os gates físicos ainda pendentes em BI-04 a BI-13, CL-11 a
CL-13 e DB-10 a DB-12. A Etapa 6/Embedded continua bloqueada pelos gates da
seção 14.

### Resultado esperado

Fazer o retorno ao app mostrar continuidade: o que mudou desde a fotografia
anterior, quais sinais a pessoa escolheu acompanhar e qual é a evidência e o
limite de cada alerta.

### Escopo fechado

1. guardar localmente até oito fotografias públicas `v1` validadas;
2. comparar somente campos literais entre a fotografia atual e a anterior;
3. permitir favoritar sinais por ID e movê-los ao início da lista;
4. responder em cada alerta `o que mudou`, `o que prova`, `onde afeta` e
   `o que não prova`;
5. declarar ausência de relação quando `effects` não trouxer elo com a carteira;
6. manter estados de carregamento, primeira fotografia, indisponibilidade e
   falha de persistência compreensíveis.

### Contratos e privacidade

- o histórico aceita somente documentos que passam por `validateLiveSnapshot`;
- snapshot com `position`, `positions`, `amount` ou outra chave proibida é
  rejeitado antes da persistência;
- favoritos guardam somente IDs públicos, sem posição, valor ou identidade;
- a comparação não interpreta número formatado nem recalcula motor financeiro;
- a camada de alerta reutiliza sinal, fonte, data, limite e `effects` existentes;
- nenhuma rede, telemetria, autenticação, nuvem ou dependência foi adicionada.

### Estado da execução

**Implementado localmente em 2026-08-31.** O app foi elevado a `v0.5.0`,
Android `versionCode 9` e iOS `buildNumber 9`. TypeScript e 37 testes móveis
passaram; o export Android/Hermes concluiu 647 módulos. O renderer web confirmou
histórico, quatro blocos de evidência, persistência degradada para sessão e a
interação de favoritar. Os viewports 375×812, 430×932, 768×1024 e 844×390
ficaram sem overflow horizontal e sem alvo interativo abaixo de 44 px. Motores,
snapshot público `v1`, parser B3 e cofre da carteira não mudaram. Não foi
gerado preview EAS deste corte.

### Próximo incremento da 5C

Implementar o simulador de aportes como ferramenta local de distribuição: a
pessoa informa um valor hipotético e explora como ele altera pesos por classe,
sem estimar retorno, sugerir ativo, selecionar produto ou criar ordem. Depois,
adicionar testes de componentes e E2E Android/iOS antes de qualquer Etapa 6.

## 22. Etapa 5C, incremento 2 — simulador local de aportes `v0.5.1`

### Resultado esperado

Permitir que a pessoa responda uma pergunta prática — “como ficariam os pesos se
eu aportasse nesta classe?” — sem alterar a carteira real e sem confundir
distribuição com previsão ou recomendação.

### Escopo fechado

1. receber um valor hipotético em formato brasileiro;
2. exigir que a pessoa escolha uma das seis classes já suportadas;
3. mostrar total da carteira e pesos por classe antes/depois;
4. incluir corretamente uma classe ainda ausente e uma carteira inicialmente
   vazia;
5. manter o cenário somente em memória, descartando o resultado quando valor ou
   classe mudarem;
6. declarar que retorno, risco, imposto, ativo, produto e ordem ficam fora da
   conta.

### Estado da execução

**Implementado localmente em 2026-08-31.** O app foi elevado a `v0.5.1`,
Android `versionCode 10` e iOS `buildNumber 10`. TypeScript e 42 testes móveis
passaram; o export Android/Hermes concluiu 649 módulos. O renderer web executou
o caminho valor → classe → comparação e confirmou o resultado e os limites nos
viewports 375×812, 430×932, 768×1024 e 844×390, sem overflow horizontal ou alvo
interativo abaixo de 44 px. Motores, snapshot público `v1`, parser B3, cofre da
carteira e persistências da `v0.5.0` não mudaram. Não foi gerado preview EAS.

### Próximo incremento da 5C

Adicionar testes de componentes para estados e interações críticas e preparar
E2E Android/iOS reproduzível. Os gates físicos pendentes continuam preservados;
Etapa 6/Embedded permanece posterior ao fechamento definido na seção 14.

## 23. Etapa 5C, incremento 3 — cobertura automatizada `v0.5.2`

### Organização fechada

1. `tests/domain/` preserva os 42 testes de contratos e funções puras em
   `node:test`;
2. `tests/components/` usa `jest-expo` e React Native Testing Library para
   estados, semântica e interação reais dos componentes;
3. `tests/e2e/` valida estaticamente identidade do app, seletores e privacidade
   dos fluxos;
4. `e2e/maestro/flows/` contém jornadas executáveis contra Android e iOS;
5. `src/testing/testIds.json` é a fonte única dos seletores compartilhados.

### Estado da execução

**Implementado localmente em 2026-08-31.** O app foi elevado a `v0.5.2`,
Android `versionCode 11` e iOS `buildNumber 11`. Passaram 42 testes de domínio,
6 testes de componentes e 4 contratos E2E; TypeScript e o export Android/Hermes
com 650 módulos também passaram. As versões oficiais compatíveis com Expo 57
ficaram em `devDependencies`, e `node_modules` voltou à junção externa prevista
para esta máquina.

Dois fluxos Maestro cobrem as quatro abas e o caminho do simulador. O ambiente
Windows portátil foi preparado fora do OneDrive com Temurin `17.0.20.1`, Maestro
`2.9.0` e ADB `37.0.1`; hashes oficiais e assinatura Google foram conferidos, e
os dois YAMLs passaram no CLI real.

`scripts/run-maestro-windows.ps1` deixa a execução reproduzível sem alterar o
`PATH` global: ele serializa instâncias, exige Android autorizado e recusa package
ou `versionName/versionCode` diferente de `app.json`. O caminho sem aparelho foi
testado e bloqueou antes de abrir qualquer app. As jornadas ainda não rodaram
porque nenhum Android estava conectado. O preview interno `v0.5.2`, build `11`,
foi concluído no EAS
[`c08e5397-427f-42c2-a163-ab5cd815cb55`](https://expo.dev/accounts/raulsallesr/projects/focuslens-br/builds/c08e5397-427f-42c2-a163-ab5cd815cb55),
commit `1c477f5`, fingerprint `4a0bc79db5a2beeb9b694f3ee8718ff13be38dff`.
O [APK direto](https://expo.dev/artifacts/eas/dvVgjSbINj4f3OdJ4CJXx_O651PcG-llvTyurlh0Ytc.apk)
expira em 2026-09-14 e teve a instalação confirmada pelo Raul. O aparelho não
estava conectado ao ADB, portanto package/versão e as jornadas não foram
verificados. O build não usou variáveis `Plain text` ou `Sensitive`. Isso mantém
E2E Android/iOS e os demais gates físicos como pendentes.

A auditoria inclui zero vulnerabilidade alta/crítica e 11 moderadas transitivas
no toolchain Expo. `npm audit fix --force` não foi aplicado: a correção sugerida
troca o projeto para Expo 46 e rompe a compatibilidade do SDK 57.

### Estado dos gates físicos

O Raul decidiu continuar nas melhorias antes de priorizar os testes físicos.
BI-04 a BI-13, CL-11 a CL-13, DB-10 a DB-12 e E2E Android/iOS permanecem
pausados e pendentes. Os dois fluxos Maestro atuais usam `clearState: true`;
não devem ser executados em uma instalação cuja carteira local precise ser
preservada. Antes da retomada, usar estado de demonstração descartável ou criar
variantes não destrutivas. Etapa 6/Embedded continua bloqueada até esses gates e
as demais condições da seção 14 serem fechados.

## 24. Etapa 5C, incremento 4 — revisão guiada da semana `v0.5.3`

### Decisão de produto em 2026-08-31

Depois de instalar o `v0.5.2/11`, o Raul preferiu continuar aumentando a
utilidade do app antes de retomar os checklists físicos. A lacuna remanescente
do item “Acompanhamento divertido e útil” da seção 5 é a trilha educativa:
`Entenda` ainda é uma explicação estática e não ajuda a percorrer a fotografia,
o recorte da carteira e um cenário como uma única rotina curta.

### Resultado esperado

Transformar os recursos já entregues em uma revisão semanal opcional que
responda, em poucos passos: o que mudou, qual é a evidência, onde existe relação
com a carteira, o que pode ser explorado em Cenários e qual é o limite da
leitura. O fluxo deve reduzir a sensação de painel longo sem criar urgência,
recompensa, streak ou incentivo a giro.

### Escopo fechado

1. oferecer uma entrada clara “Revisar a semana” a partir de Hoje;
2. reutilizar o sinal selecionado, comparação literal, fonte, data, `effects` e
   impactos já calculados, sem criar nova interpretação financeira;
3. tornar `Entenda` contextual, com acesso ao tópico relacionado e retorno
   previsível à exploração;
4. conduzir para Cenários somente como hipótese educacional, sem preencher valor,
   classe ou choque em nome da pessoa;
5. usar revelação progressiva, feedback visual de toque, rótulos acessíveis e
   alvos mínimos de 44 px, preservando as quatro abas;
6. manter todo o estado da revisão apenas em memória e descartar a sequência ao
   reiniciar o app;
7. cobrir navegação, estados sem histórico/efeito e limites com testes de
   componentes, além dos gates móveis existentes.

### Fora de escopo

- alterar motores Python, regras financeiras ou o snapshot público `v1`;
- adicionar persistência, dependência, rede, telemetria ou sincronização;
- calcular retorno, risco, probabilidade, produto, ordem ou recomendação;
- transformar educação em checklist obrigatório, gamificação ou notificação;
- executar automaticamente Maestro, limpar estado do app ou fechar gates
  físicos por inferência;
- iniciar Etapa 6, Embedded, autenticação ou Open Finance.

### Gate do incremento

`npm run typecheck`, `npm test`, `npm run export:android` e validação visual nos
viewports já usados pelo projeto. O handoff deve registrar separadamente o que
foi comprovado localmente e o que continua dependendo de aparelho real.

### Estado da execução

**Implementado localmente em 2026-08-31.** A Home ganhou uma entrada opcional
depois da fotografia e do histórico, sem deslocar o recorte pessoal da primeira
dobra. O sinal escolhido em Hoje inicia uma sequência de cinco passos em
Entenda: comparação literal, evidência, relação com posições, exploração em
Cenários e limite. Favorito, fonte, data, `effects`, impactos e posições vêm
somente dos objetos já compostos em memória.

O progresso vive em `App.tsx` e desaparece ao reiniciar o app. A ida a Cenários
preserva valor, classe e choque que já estavam na tela, não preenche hipótese e
oferece retorno explícito à etapa final. Sem duas fotografias, a revisão declara
ausência de comparação; sem efeito, mantém a relação vazia e não inventa posição
ou impacto. A explicação geral de Entenda continua disponível sob revelação
progressiva, e as quatro abas foram preservadas.

O app foi elevado a `v0.5.3`, Android `versionCode 12` e iOS `buildNumber 12`.
Passaram TypeScript, 42 testes de domínio, 10 de componentes e 4 contratos E2E.
O export Android/Hermes concluiu 651 módulos fora do sandbox depois de a primeira
tentativa reproduzir o `spawn EPERM` conhecido. A jornada completa passou em
375×812, 430×932, 768×1024 e 844×390, sem overflow horizontal nem alvo visível
abaixo de 44 px.

Nenhum Maestro ou gate físico foi executado. O preview instalado continua sendo
o `v0.5.2/11`; BI-04 a BI-13, CL-11 a CL-13, DB-10 a DB-12 e E2E Android/iOS
permanecem pausados e pendentes.

## 25. Etapa 5C, incremento 5 — “Quanto vira?” `v0.5.4`

### Decisão de produto em 2026-08-31

O Raul identificou que o app estava tecnicamente sólido, mas ainda exigia
conhecimento prévio para saber o que explorar. A próxima utilidade deve começar
por uma pergunta reconhecível para iniciantes e permitir brincar com números
sem tocar carteira, produto ou motor de mercado.

### Escopo fechado

1. receber valor inicial, aporte mensal, taxa efetiva anual e prazo;
2. converter a taxa anual para equivalente mensal e considerar aportes ao fim
   de cada mês;
3. separar valor final, capital colocado e juros do cenário;
4. mostrar marcos de evolução com rótulos e valores, sem depender apenas de cor;
5. oferecer inflação somente sob ação explícita, sem misturá-la ao resultado
   nominal;
6. manter os valores apenas na sessão e respeitar o modo discreto.

### Estado da execução

**Implementado no corte consolidado de 2026-08-31.** `moneyLab.ts` concentra a
aritmética pura; `MoneyLabPanel.tsx` abre Cenários com um exemplo fictício,
editável e imediatamente responsivo. Taxa constante é apresentada como
hipótese mecânica, nunca como retorno esperado, promessa ou taxa indicada. Este
marco lógico corresponde a `v0.5.4`, Android `versionCode 13` e iOS
`buildNumber 13`; não houve build EAS intermediário.

## 26. Etapa 5C, incremento 6 — meta e tempo `v0.5.5`

### Escopo fechado

1. inverter a mesma fórmula para responder quanto aportar por mês até uma meta;
2. impedir aporte negativo quando o valor inicial já alcançaria a meta na
   hipótese;
3. comparar começar agora com esperar um, três ou cinco anos;
4. manter o valor inicial parado e pular aportes durante a espera, deixando essa
   convenção explícita;
5. não transformar a meta calculada em plano financeiro ou garantia.

### Estado da execução

**Implementado no mesmo corte consolidado.**
`calculateRequiredMonthlyContribution` e `compareDelayedStart` reutilizam a
taxa mensal equivalente do incremento anterior e não acessam carteira,
snapshot, storage ou rede. Este marco lógico corresponde a `v0.5.5`, Android
`versionCode 14` e iOS `buildNumber 14`; não houve build EAS intermediário.

## 27. Etapa 5C, incremento 7 — inflação, hábito e intuição `v0.5.6`

### Escopo fechado

1. traduzir o valor final para dinheiro do início usando inflação escolhida
   pela pessoa;
2. converter um valor diário, semanal ou mensal para equivalente médio mensal,
   sem classificar o hábito como certo ou errado;
3. pedir um palpite antes de comparar +1 p.p. de taxa com +R$ 150 de aporte
   mensal sobre a mesma base;
4. explicar que o vencedor depende dos números e não torna mais taxa possível,
   adequada ou preferível;
5. manter as cinco perguntas sob revelação progressiva, com feedback de toque,
   campos controlados e alvos mínimos de 44 px.

### Fora de escopo dos três incrementos

- alterar motores Python, fórmulas já aprovadas, cofre, importador B3,
  persistências ou snapshot público `v1`;
- consultar taxa, carteira, produto ou fonte externa para preencher hipóteses;
- adicionar dependência, rede, telemetria, recomendação, promessa, produto,
  ordem, autenticação, Open Finance ou Embedded;
- rodar Maestro automaticamente ou inferir aprovação física.

### Gate consolidado

O app termina em `v0.5.6`, Android `versionCode 15` e iOS `buildNumber 15`.
Passaram `npm run typecheck`, 51 testes de domínio, 16 de componentes, 4
contratos E2E e `npm run export:android`; o bundle Android/Hermes possui 653
módulos. As cinco perguntas, a inflação opcional e a revelação do desafio foram
percorridas em 375×812, 430×932, 768×1024 e 844×390. Documento, body e painel
mantiveram a largura do viewport, e nenhum alvo interativo visível ficou abaixo
de 44 px.

O primeiro export e a primeira abertura do Playwright reproduziram,
respectivamente, `spawn EPERM` e `WinError 5` dentro do sandbox; ambos passaram
fora dele sem mudança de código. Nenhum preview EAS, Maestro ou gate físico foi
executado. O preview instalado continua sendo `v0.5.2/11`; BI-04 a BI-13,
CL-11 a CL-13, DB-10 a DB-12 e E2E Android/iOS permanecem pausados e pendentes.

## 28. Etapa 5C, incremento 8 — o poder do tempo `v0.5.7`

### Resultado esperado

Transformar prazo em uma variável que a pessoa consegue tocar e compreender:
quando o valor inicial dobra, quais marcos aparecem e como a projeção muda ao
avançar ou recuar o horizonte.

### Escopo fechado

1. comparar a dobra do valor inicial com e sem novos aportes;
2. localizar R$ 10 mil, R$ 50 mil e R$ 100 mil somente dentro do horizonte;
3. mostrar capital e juros no marco alcançado, além do tempo aproximado;
4. oferecer régua de 1 a 50 anos com pontos tocáveis e botões menos/mais;
5. manter alternativa acessível ao toque direto, sem gesto obrigatório;
6. declarar que taxa constante e aportes sem interrupção não garantem data.

### Estado da execução

**Implementado no corte consolidado de 2026-09-01.**
`calculateDoublingTime` e `calculateMilestoneTimeline` operam apenas sobre os
números digitados. A régua altera o prazo inteiro da sessão e atualiza o
resultado imediatamente, sem dependência nova ou gesto horizontal conflitante
com a rolagem principal. Este marco lógico corresponde a `v0.5.7`, Android
`versionCode 16` e iOS `buildNumber 16`; não houve build EAS intermediário.

## 29. Etapa 5C, incremento 9 — dinheiro que entra `v0.5.8`

### Escopo fechado

1. converter taxa anual efetiva para mensal sem dividir por 12;
2. mostrar o equivalente de um mês somente sobre o valor inicial informado;
3. comparar o mesmo cenário sem/com um aporte extra;
4. permitir extra único no início ou repetido ao fim de cada ano;
5. explicar que equivalente mensal não significa pagamento, renda ou liquidez;
6. não associar o valor a instituição, produto ou 13º real da pessoa.

### Estado da execução

**Implementado no mesmo corte consolidado.**
`calculateMonthlyYieldEquivalent` reutiliza `effectiveMonthlyRate` e
`simulateExtraContribution` aplica o extra na convenção explicitada, mantendo
uma base comparável. Este marco lógico corresponde a `v0.5.8`, Android
`versionCode 17` e iOS `buildNumber 17`; não houve build EAS intermediário.

## 30. Etapa 5C, incremento 10 — caminho da reserva `v0.5.9`

### Escopo fechado

1. receber reserva atual, gasto essencial mensal e aporte mensal;
2. mostrar quantos meses o valor atual cobre por divisão direta;
3. permitir que a própria pessoa escolha três, seis ou doze meses como meta;
4. calcular valor faltante e meses inteiros até a meta, sem rendimento;
5. declarar ausência de prazo quando o aporte é zero e a meta não foi atingida;
6. não recomendar tamanho de reserva nem ler automaticamente a carteira local.

### Estado da execução

**Implementado no mesmo corte consolidado.** `calculateReserveJourney` não usa
taxa, produto ou carteira. Valores e meta ficam no `MoneyLabSession` e somem ao
reiniciar. Este marco lógico corresponde a `v0.5.9`, Android `versionCode 18` e
iOS `buildNumber 18`; não houve build EAS intermediário.

## 31. Etapa 5C, incremento 11 — laboratório completo `v0.6.0`

### Escopo fechado

1. comparar manter só o valor inicial com fazer os aportes informados;
2. revelar inflação apenas quando solicitada;
3. revelar custo anual hipotético apenas quando solicitado e limitá-lo à taxa;
4. tratar custo como redução mecânica de taxa, nunca tributo ou taxa de produto;
5. explicar por que aporte e custo se acumulam ao longo do tempo;
6. preservar as nove perguntas em duas camadas progressivas dentro de Cenários;
7. manter as quatro abas, modo discreto e todo o estado apenas na sessão.

### Fora de escopo dos quatro incrementos

- alterar motores Python, snapshot público `v1`, cofre, importador B3,
  persistências, histórico ou favoritos;
- consultar taxa externa, carteira ou produto para preencher hipótese;
- adicionar dependência, rede, telemetria, retorno previsto, recomendação,
  ordem, autenticação, Open Finance ou Embedded;
- modelar imposto sem produto/regime ou chamar custo hipotético de taxa real;
- rodar Maestro automaticamente ou inferir aprovação física.

### Gate consolidado

O app termina em `v0.6.0`, Android `versionCode 19` e iOS `buildNumber 19`.
Passaram `npm run typecheck`, 61 testes de domínio, 22 de componentes, 4
contratos E2E e `npm run export:android`; o bundle Android/Hermes possui 654
módulos. As quatro trilhas novas foram percorridas em 375×812, 430×932,
768×1024 e 844×390. Documento, body e painel mantiveram a largura do viewport,
e nenhum alvo interativo visível ficou abaixo de 44 px.

O primeiro export e a primeira abertura do Playwright reproduziram,
respectivamente, `spawn EPERM` e `WinError 5` dentro do sandbox; ambos passaram
fora dele sem mudança de código. Nenhum preview EAS, Maestro ou gate físico foi
executado. O preview instalado continua sendo `v0.5.2/11`; BI-04 a BI-13,
CL-11 a CL-13, DB-10 a DB-12 e E2E Android/iOS permanecem pausados e pendentes.

## 32. Etapa 5C, incremento 12 — Cenários por intenção `v0.6.1`

### Decisão de produto em 2026-09-01

Depois de nove caminhos educacionais, o problema deixou de ser falta de
conteúdo e passou a ser orientação. Empilhar mais painéis faria uma pessoa
iniciante escolher pela posição na tela, não pela pergunta que deseja responder.

### Escopo fechado

1. abrir Cenários com três intenções reconhecíveis: começar do zero, enxergar o
   caminho e testar situações da vida real;
2. mostrar somente uma família do laboratório por vez, sem remover nenhuma das
   experiências existentes;
3. preservar a família e todos os valores ao trocar de aba, somente na sessão;
4. manter aporte por classe e sensibilidade da carteira como blocos separados;
5. manter as quatro abas, feedback de toque, rótulos e alvos mínimos de 44 px.

### Estado da execução

**Implementado localmente em 2026-09-01.** `MoneyLabIntentHub` controla apenas
qual família é apresentada. `MoneyLabPanel`, `MoneyLabExpansionPanel` e a nova
família cotidiana continuam recebendo a mesma `MoneyLabSession` de `App.tsx`.
Nenhuma rota, persistência ou navegação de primeiro nível foi criada. Este marco
lógico corresponde a `v0.6.1`, Android `versionCode 20` e iOS `buildNumber 20`;
não houve build EAS intermediário.

## 33. Etapa 5C, incremento 13 — plano que respira `v0.6.2`

### Escopo fechado

1. comparar o aporte mensal fixo com um aporte que aumenta uma porcentagem a
   cada ano;
2. permitir uma pausa opcional de zero, três, seis ou doze meses no meio do
   prazo, sem transformar aportes pulados em dívida ou reposição automática;
3. separar valor final, total colocado, juros, aportes pulados e aporte mensal
   previsto no último ano;
4. manter a mesma taxa efetiva anual informada pela pessoa e a convenção de
   aporte ao fim do mês;
5. declarar renda, capacidade futura e continuidade como limites da conta.

### Estado da execução

**Implementado no mesmo corte consolidado.**
`simulateFlexibleContributionPlan` executa um laço mensal puro, aplica o aumento
no início de cada ano e zera apenas os aportes dentro da pausa. O resultado é
comparado com `simulateCompoundGrowth` sobre a mesma base. Este marco lógico
corresponde a `v0.6.2`, Android `versionCode 21` e iOS `buildNumber 21`; não
houve build EAS intermediário.

## 34. Etapa 5C, incremento 14 — parcelado sem mistério `v0.6.3`

### Escopo fechado

1. receber preço à vista, valor de cada parcela e quantidade de parcelas;
2. mostrar total parcelado e diferença literal contra o preço à vista;
3. quando o parcelado custa mais, calcular a taxa mensal que iguala o valor
   presente das parcelas ao preço à vista e seu equivalente anual efetivo;
4. quando o parcelado não custa mais, não inventar uma taxa positiva;
5. explicitar a convenção da primeira parcela em um mês e excluir tarifas,
   atraso, limite, inflação e uso alternativo do dinheiro;
6. não recomendar forma de pagamento, produto ou crédito.

### Fora de escopo dos três incrementos

- alterar motores Python, fórmulas financeiras existentes, snapshot público
  `v1`, cofre, importador B3, carteira, histórico, favoritos ou persistências;
- preencher valores com carteira, produto, instituição ou fonte externa;
- adicionar dependência, rede, telemetria, retorno previsto, recomendação,
  ordem, autenticação, Open Finance ou Embedded;
- rodar Maestro automaticamente ou inferir aprovação física.

### Gate consolidado

O app termina em `v0.6.3`, Android `versionCode 22` e iOS `buildNumber 22`.
Passaram `npm run typecheck`, 66 testes de domínio, 30 de componentes, 4
contratos E2E e `npm run export:android`; o bundle Android/Hermes possui 656
módulos. As três famílias, o plano flexível e o parcelamento foram percorridos
em 375×812, 430×932, 768×1024 e 844×390 com movimento reduzido: documento,
body e painel mantiveram a largura do viewport e nenhum alvo interativo visível
ficou abaixo de 44 px.

O primeiro export e a primeira abertura do Playwright reproduziram,
respectivamente, `spawn EPERM` e `WinError 5` dentro do sandbox; ambos passaram
fora dele sem mudança de código. Nenhum preview EAS, Maestro ou gate físico foi
executado. O preview instalado continua sendo `v0.5.2/11`; BI-04 a BI-13,
CL-11 a CL-13, DB-10 a DB-12 e E2E Android/iOS permanecem pausados e pendentes.

## 35. Etapa 5C, incremento 15 — dinheiro que dura `v0.6.4`

### Decisão de produto em 2026-09-01

As doze experiências originalmente propostas ao Raul já estavam cobertas até
`v0.6.3`. A continuação deve acrescentar uma pergunta nova e reconhecível, não
reembalar acumulação: quanto tempo um saldo atravessa retiradas mensais dentro
de um horizonte escolhido.

### Escopo fechado

1. receber saldo inicial, retirada mensal, taxa efetiva anual e horizonte;
2. converter a taxa anual para equivalente mensal, creditar o crescimento e
   realizar a retirada ao fim de cada mês;
3. mostrar mês de esgotamento ou saldo remanescente, total retirado, crescimento
   creditado e marcos dentro do horizonte;
4. oferecer reajuste anual da retirada somente sob ação explícita, usando uma
   inflação escolhida pela pessoa;
5. declarar que a faixa de fôlego representa duração mecânica dentro do
   horizonte, não probabilidade ou retirada segura;
6. manter ferramenta, valores e opção avançada somente na `MoneyLabSession`.

### Fora de escopo

- ler carteira, snapshot, produto, instituição, renda ou expectativa de vida;
- prever retorno, inflação, imposto, volatilidade ou mudança futura de gastos;
- recomendar retirada, produto ou estratégia;
- alterar motores Python, snapshot público `v1`, cofre, importador B3 ou
  persistências existentes;
- adicionar dependência, rede, telemetria, autenticação, Open Finance ou
  Embedded;
- executar Maestro ou inferir aprovação física.

### Estado da execução e gate

**Implementado localmente em 2026-09-01.** `simulateWithdrawalLongevity` é um
laço mensal puro: aplica a taxa mensal equivalente, retira no fim do mês e,
quando solicitado, reajusta a retirada depois de cada doze meses completos. A
linha do tempo reutiliza somente entradas da sessão e não acessa provider,
carteira ou storage.

O app termina em `v0.6.4`, Android `versionCode 23` e iOS `buildNumber 23`.
Passaram `npm run typecheck`, 70 testes de domínio, 33 de componentes, 4
contratos E2E e `npm run export:android`; o bundle Android/Hermes possui 656
módulos. A jornada, inclusive inflação opcional, foi percorrida em 375×812,
430×932, 768×1024 e 844×390 com movimento reduzido. Documento, body e painel
mantiveram a largura do viewport, e nenhum controle visível ficou abaixo de
44 px. A inspeção visual corrigiu uma folga excessiva do campo opcional antes
do gate final.

O export e o Playwright reproduziram, respectivamente, `spawn EPERM` e
`WinError 5` dentro do sandbox e passaram fora dele sem mudança funcional.
Nenhum preview EAS, Maestro ou gate físico foi executado. O preview instalado
continua `v0.5.2/11`; BI-04 a BI-13, CL-11 a CL-13, DB-10 a DB-12 e E2E
Android/iOS permanecem pausados e pendentes.
