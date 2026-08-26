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

## 11. Próxima execução — Etapa 1

Ordem de trabalho:

1. definir matematicamente “mudança relevante” por indicador;
2. criar motor puro que ordena as revisões;
3. modelar os quatro estados de atualização;
4. compor o bloco “O que mudou” na seção Focus;
5. adicionar testes de regra, datas, ausência de dado e UI;
6. revisar a tela em desktop e mobile;
7. preparar README, imagens e release `v1.12`;
8. auditar o repositório antes de qualquer mudança de visibilidade.

Nenhuma decisão de fonte, arquitetura ou identidade visual está pendente para
começar essa etapa.
