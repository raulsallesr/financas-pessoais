# FocusLens BR v2.0 — release candidate

O FocusLens BR reúne expectativas, curva prefixada, cenário mecânico e
carteira local em uma experiência única: Resumo → Expectativas → Curva →
Carteira.

## O que entra na v2.0

- Resumo integrado que escolhe a melhor leitura disponível sem recalcular os
  motores e mantém duas–quatro provas, datas, limite e condição de mudança;
- jornada de página única com quatro âncoras e falha isolada por fonte;
- choque paralelo de −100 a +100 bps sobre a fotografia atual da curva, sem
  estimar probabilidade, preço ou retorno;
- metodologia canônica que separa evidência, hipótese, contexto externo e
  dados pessoais mantidos somente na sessão;
- captura principal, diagrama técnico e texto de publicação;
- auditoria de privacidade, segredos, licenças, dependências e histórico Git.

## Arquitetura preservada

Os motores de Focus Semanal (`v1.12`), Curva Tesouro (`v1.13`) e Focus × Curva
(`v1.14`) continuam como fontes dos cálculos. `focuslens/core/resumo_integrado.py` apenas
orquestra os contratos. `focuslens/core/curva_cenarios.py` trabalha sobre uma cópia descritiva
da fotografia atual e não altera cache, D-5/D-21, Radar ou carteira.

## Qualidade

- 185 testes automatizados;
- `py_compile`, `pip check` e `git diff --check` aprovados;
- primeira dobra validada em 375, 768, 1024, 1440 e 844×390 px;
- nenhum significado transmitido apenas por cor;
- nenhum segredo, dado pessoal ou arquivo real de carteira encontrado;
- `pip-audit` sem vulnerabilidade conhecida na resolução desta release.

## Artefatos

- captura: [`../assets/focuslens-br-v2.0.png`](../assets/focuslens-br-v2.0.png);
- arquitetura: [`../assets/arquitetura-focuslens-v2.0.svg`](../assets/arquitetura-focuslens-v2.0.svg);
- metodologia: [`../product/METODOLOGIA_FOCUSLENS.md`](../product/METODOLOGIA_FOCUSLENS.md);
- auditoria: [`AUDITORIA_PUBLICACAO_V2.0.md`](AUDITORIA_PUBLICACAO_V2.0.md);
- LinkedIn: [`POST_LINKEDIN_FOCUSLENS_V2.0.md`](POST_LINKEDIN_FOCUSLENS_V2.0.md).

## Estado da publicação

O código permanece como release candidate e o repositório é público desde
2026-09-02, sob licença MIT. A tag/release `v2.0` continua opcional e separada;
o e-mail não mascarado dos metadados antigos foi aceito para preservar o
histórico e seus hashes.
