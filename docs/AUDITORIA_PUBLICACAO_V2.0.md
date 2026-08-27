# Auditoria de publicação — FocusLens BR v2.0

**Data da auditoria:** 27/08/2026

**Base auditada:** `main` em `536916c`

**Estado:** tecnicamente aprovado como release candidate; repositório mantido
privado até as decisões de governança descritas abaixo.

Esta é uma auditoria técnica de publicação, não um parecer jurídico.

## Veredito

O código, os dados versionados, os ativos visuais e as dependências não
apresentaram segredo, dado pessoal, arquivo de carteira, extensão sensível ou
vulnerabilidade conhecida nos testes executados. O pacote pode ser versionado
e apresentado como release candidate.

A abertura pública e a tag `v2.0` ficam pendentes de duas decisões do titular:

1. escolher a licença do código — por exemplo, uma licença aberta ou a
   manutenção explícita de todos os direitos reservados;
2. aceitar a exposição de um e-mail de autor não mascarado presente nos
   metadados de commits ou autorizar uma reescrita controlada do histórico.

Reescrita de histórico e mudança de visibilidade não foram executadas.

## Evidências por gate

| Gate | Resultado | Evidência |
|---|---|---|
| Árvore atual | Aprovado | 107 arquivos no candidato final (102 da base e cinco novos); nenhum caminho `.env`, XLSX, PDF, chave, certificado ou banco local |
| Segredos e PII | Aprovado | nenhum token conhecido, chave privada, credencial atribuída, CPF/CNPJ válido ou padrão equivalente encontrado |
| Histórico Git | Aprovado com ressalva | conteúdo e caminhos dos refs alcançáveis limpos; um e-mail de autor não mascarado permanece nos metadados |
| Caches públicos | Aprovado | 90 registros Focus e 225 pontos de curva; somente campos públicos documentados |
| Carteira | Aprovado | importação XLSX em memória; identificadores descartados; nenhum valor ou arquivo pessoal versionado |
| Dependências | Aprovado | `pip check` limpo; `pip-audit 2.10.1 -r requirements.txt` sem vulnerabilidade conhecida nesta data |
| Licenças de dependências | Aprovado | árvore instalada com 39 distribuições; licenças permissivas ou compatíveis identificadas, sem GPL/AGPL detectada |
| Fontes e atribuição | Aprovado | BACEN/Focus e Tesouro sob ODbL; atribuições visíveis; EIA/FRED citado; Binance e RSS consumidos sem republicar bases ou corpos editoriais |
| Ativos visuais | Aprovado | PNG obtido do app real e SVG autoral, sem fonte, foto, logotipo ou biblioteca visual externa |
| Workflows | Aprovado | ações oficiais; permissões de escrita usadas somente para versionar os dois caches públicos |
| Licença do código | Decisão pendente | não existe arquivo `LICENSE`; sem licença, terceiros não recebem permissão explícita de reutilização |
| Visibilidade | Preservada | consulta anônima ao GitHub retornou 404 e o push autenticado continuou funcional: repositório privado |

## Dados versionados

### `dados/focus_cache.json`

- campos: indicador, referência, data de coleta, mediana, média, mínimo,
  máximo, desvio-padrão e número de respondentes;
- origem: Sistema de Expectativas de Mercado/BACEN;
- não contém instituição respondente, CPF, CNPJ, conta ou posição pessoal.

### `dados/curva_prefixada_cache.json`

- campos: data-base, tipo de título, vencimento, taxas, preços unitários e
  fonte;
- origem: Tesouro Transparente;
- não contém custódia, investidor, corretora ou posição individual.

## Dependências e licenças

Dependências diretas verificadas no ambiente da auditoria:

| Pacote | Versão instalada | Licença declarada |
|---|---:|---|
| Streamlit | 1.56.0 | Apache-2.0 |
| Requests | 2.34.2 | Apache-2.0 |
| Pandas | 3.0.5 | BSD-3-Clause |
| openpyxl | 3.1.5 | MIT |

A árvore transitiva instalada totalizou 39 distribuições. Foram observadas
licenças Apache, BSD, MIT, MPL-2.0, PSF e equivalentes permissivas. O resultado
é uma fotografia do ambiente em 27/08/2026; vulnerabilidades e metadados podem
mudar e devem ser reavaliados em cada release.

## Fontes públicas e direitos de conteúdo

- **BACEN/Focus:** o catálogo oficial declara Open Data Commons ODbL e o app
  mantém fonte e datas junto da leitura.
- **Tesouro Transparente:** o metadado CKAN declara `odc-odbl`; o cache mantém
  atribuição por registro e a metodologia registra o recorte utilizado.
- **Brent:** a série DCOILBRENTEU identifica a EIA como fonte e solicita
  citação; o projeto exibe a atribuição e não versiona uma cópia da série.
- **Binance:** somente a API pública de mercado é consultada; não há base bruta
  redistribuída no repositório.
- **Notícias:** o app exibe título, veículo, horário e link do RSS. Corpo,
  imagem e paywall não são republicados; análise sob demanda é efêmera.
- **Imagens da release:** a captura é do próprio app e o diagrama é SVG
  produzido no repositório com tipografia do sistema.

## Comandos e verificações executados

- varredura do estado atual e dos patches de todos os refs alcançáveis por
  padrões de chaves, tokens, credenciais, CPF e CNPJ, sem imprimir conteúdo;
- inspeção dos caminhos atuais e históricos por extensões sensíveis;
- inventário estrutural dos dois caches, exibindo apenas chaves e contagens;
- inventário de licenças da árvore de dependências instalada;
- `pip-audit 2.10.1 -r requirements.txt` em ambiente temporário isolado;
- `pip check`, suíte completa, `py_compile` e `git diff --check`;
- validação do PNG real em 375, 768, 1024, 1440 e 844×390 px;
- parsing XML e renderização real do SVG técnico;
- consulta anônima de visibilidade do repositório no GitHub.

## Checklist antes de abrir o repositório

- [x] segredos e dados pessoais auditados;
- [x] histórico e caminhos removidos auditados;
- [x] caches públicos inspecionados;
- [x] dependências e vulnerabilidades auditadas;
- [x] atribuições das fontes documentadas;
- [x] captura principal e imagem técnica geradas;
- [x] README, release notes e texto de LinkedIn preparados;
- [ ] licença do código decidida e registrada;
- [ ] exposição do e-mail histórico aceita ou saneada;
- [ ] tag e release `v2.0` criadas;
- [ ] visibilidade alterada mediante autorização explícita;
- [ ] links públicos conferidos antes do post.
