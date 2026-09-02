# Auditoria de publicação — FocusLens BR

**Data da auditoria:** 02/09/2026

**Base funcional auditada:** `f2ed931` (`main`)

**Cortes apresentados:** Streamlit `v2.0` e mobile `v0.6.4/23`

**Estado:** repositório público por ação explícita do titular; CI público
`quality` verde, prerelease `v0.6.4-beta` publicada e `main` protegida.

Esta é uma auditoria técnica de publicação, não um parecer jurídico nem uma
aprovação para distribuição em loja.

## Veredito

O candidato possui licença MIT, narrativa pública atual, três capturas reais e
uma demonstração curta do app em MP4/GIF, lint Python, cobertura mensurada e CI
para as duas stacks. A varredura da árvore e do histórico não encontrou segredo,
CPF/CNPJ válido, arquivo de carteira ou extensão sensível.

O histórico Git foi preservado. Um endereço pessoal continua presente em
metadados antigos; os novos commits já usam o endereço `noreply` oficial do
GitHub. Isso evita uma reescrita de 63 commits e a troca de todos os hashes.

A abertura pública foi executada pelo titular em 2026-09-02. Tag/release e as
regras da `main` continuam opcionais e pendentes. O Raul aceitou manualmente o
beta no POCO e dispensou USB/ADB e iOS como bloqueadores do portfólio. Os gates
formais não executados continuam sem evidência; por isso o projeto deve ser
apresentado como **beta funcional**, não como app validado em produção.

## Evidências por gate

| Gate | Resultado | Evidência |
|---|---|---|
| Árvore atual | Aprovado | 212 arquivos rastreados/candidatos; raiz reduzida a entrada, configuração, licença e handoff |
| Segredos e PII | Aprovado | zero arquivo com os padrões auditados de chave privada, credencial atribuída, token conhecido ou CPF/CNPJ válido |
| Histórico Git | Aprovado com ressalva aceita | zero extensão sensível e zero família de padrão de segredo; um e-mail antigo não mascarado permanece nos metadados |
| Licença do projeto | Aprovado | `LICENSE` MIT, copyright 2026 Raul Rolim |
| Identidade futura | Aprovado | commit `f2ed931` criado com GitHub `noreply`; histórico não reescrito |
| Caches públicos | Aprovado | 96 registros Focus e 225 pontos de curva, somente com campos públicos documentados |
| Carteira | Aprovado | XLSX processado localmente; identificadores descartados; nenhum valor ou arquivo pessoal versionado |
| Python | Aprovado | Ruff limpo; 194 testes; cobertura de branches em 86,1%, acima do piso de 85% |
| Mobile | Aprovado localmente | TypeScript, 70 testes de domínio, 33 de componentes, 4 contratos E2E e export Android com 656 módulos |
| CI | Aprovado | workflow público `quality` executa Python e mobile; resultado remoto conferido verde |
| Dependências Python | Aprovado | `pip check` limpo; `pip-audit 2.10.1` sem vulnerabilidade conhecida |
| Dependências mobile | Aprovado com ressalva | zero vulnerabilidade alta/crítica; 11 moderadas transitivas no toolchain Expo/UUID |
| Ativos visuais | Aprovado | três PNGs e demo real de 21,2 s em MP4/GIF, com fotografia pública e carteira fictícia, sem imagem externa |
| EAS Android | Concluído + aceite manual | preview `v0.6.4/23` terminou `FINISHED`; Raul aceitou o app atual no POCO, sem associação independente de package/build por ADB |
| Visibilidade | Pública e protegida | repositório aberto pelo titular em 2026-09-02; prerelease `v0.6.4-beta` publicada e ruleset `Proteção da main` ativo |

## Cobertura e qualidade automatizada

O workflow `.github/workflows/tests.yml` possui dois jobs independentes:

1. **Python:** instala `requirements-dev.txt`, executa Ruff, roda a suíte com
   cobertura de branches e publica `coverage.xml` como artefato do job;
2. **Mobile:** usa Node 24, instalação reproduzível por `npm ci`, TypeScript,
   todos os testes e export Android/Hermes.

O piso de cobertura está em `pyproject.toml`. Ele vale sobre a aplicação
Python inteira, incluindo apresentação e scripts; testes não entram no
denominador. A medição do candidato foi 86,1%, sem exclusão artificial de
módulo pouco coberto.

Os 194 testes Python e os 107 testes mobile totalizam **301 testes
automatizados**. Maestro não foi executado nesta auditoria.

## Dependências

Dependências diretas Python verificadas no ambiente:

| Pacote | Versão instalada | Licença declarada |
|---|---:|---|
| Streamlit | 1.56.0 | Apache-2.0 |
| Requests | 2.34.2 | Apache-2.0 |
| Pandas | 3.0.5 | BSD-3-Clause |
| openpyxl | 3.1.5 | MIT |

`pip-audit 2.10.1 -r requirements.txt` não encontrou vulnerabilidade conhecida
em 02/09/2026.

O `npm audit`, inclusive com `--omit=dev`, reportou 11 vulnerabilidades
moderadas na cadeia `uuid → xcode → @expo/config-plugins`. Não existe achado
alto ou crítico. O reparo automático sugerido exige uma mudança incompatível
com o Expo SDK 57; `npm audit fix --force` não foi aplicado. Esse risco deve ser
reavaliado numa atualização coordenada do Expo e antes de distribuição em loja,
mas não exige quebrar o beta apenas para produzir um número verde.

## Dados, fontes e ativos

### `dados/focus_cache.json`

- 96 registros de expectativas;
- origem: Sistema de Expectativas de Mercado/BACEN;
- sem instituição respondente, documento, conta ou posição pessoal.

### `dados/curva_prefixada_cache.json`

- 225 pontos de curva;
- origem: Tesouro Transparente;
- sem custódia, investidor, corretora ou posição individual.

O snapshot mobile público transporta somente leitura, fonte, data, evidência e
efeitos por classe. Carteira, histórico privado, favoritos e estados de
simulação ficam fora desse artefato.

As imagens `focuslens-mobile-v0.6.4-*.png` foram capturadas do renderer web da
mesma árvore React Native. Elas usam o snapshot público e a demonstração
fictícia; não contêm captura de aparelho ou dado do titular.

O MP4 `focuslens-mobile-v0.6.4-demo.mp4` tem 21,2 segundos, `720×1560`, H.264,
sem áudio e cerca de 1,3 MB. O GIF correspondente tem `360×780` e cerca de
1,0 MB. Ambos percorrem somente estado sintético da sessão e encerram no limite
da leitura; os quadros temporários usados na composição não são versionados.

## Comandos e verificações executados

- `ruff check .`;
- `pytest tests/ -q --cov=.` com branch coverage e piso de 85%;
- `pip check`;
- `pip-audit 2.10.1 -r requirements.txt`;
- `npm run typecheck`;
- `npm test`;
- `npm run export:android` fora do sandbox após o `spawn EPERM` conhecido;
- `npm audit --omit=dev --audit-level=high` e auditoria da árvore completa;
- varredura do candidato e dos patches alcançáveis por padrões de segredo e
  documentos válidos, sem imprimir conteúdo encontrado;
- inspeção de caminhos atuais e históricos por extensões sensíveis;
- validação de links locais, dimensões dos PNGs e `git diff --check`;
- decodificação integral do MP4 e do GIF com FFmpeg, além de inspeção visual
  dos quadros inicial, intermediários e final.

## Estado da abertura pública

- [x] licença MIT registrada;
- [x] identidade futura alterada para GitHub `noreply`;
- [x] histórico preservado por decisão explícita;
- [x] CI Python/mobile configurado;
- [x] cobertura real medida e protegida por piso;
- [x] README, capturas, MP4/GIF e texto de LinkedIn preparados;
- [x] segredos, PII, caches e dependências reavaliados;
- [x] fazer push e observar o workflow `quality` verde;
- [x] tornar o repositório público mediante ação explícita;
- [ ] abrir o link em sessão anônima e conferir README, licença e imagens;
- [x] criar a prerelease pública `v0.6.4-beta`, sem APK temporário anexado;
- [x] configurar ruleset da `main` sem bloquear os workflows que atualizam os
  caches públicos automaticamente.

`CONTRIBUTING.md`, Codecov e reescrita do histórico não são necessários para a
primeira publicação. Se contribuições externas forem abertas depois, esses
itens podem ser reavaliados com base no uso real.
