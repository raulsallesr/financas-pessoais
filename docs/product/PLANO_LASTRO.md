# Plano — Lastro (plataforma) e módulo Ativos B3

> Nome provisório. **Lastro** é a plataforma. O FocusLens BR passa a ser o módulo
> **Macro**: seu plano continua em [`PLANO_FOCUSLENS.md`](PLANO_FOCUSLENS.md) e os
> princípios dele seguem valendo para ele.

## 1. Visão

Uma plataforma pessoal de inteligência financeira com dois módulos que conversam:

- **Macro (FocusLens).** Expectativas do Focus, curva do Tesouro, radar e carteira
  local.
- **Ativos B3.** Métricas fundamentalistas, screener, score quantitativo, valor
  intrínseco estimado, ranking de ETFs e montagem de carteira diversificada.

O Macro alimenta o Ativos:
- a curva do Tesouro dá a taxa livre de risco do valuation e o prêmio NTN-B dos FIIs;
- o CDI é o benchmark de Sharpe e Sortino;
- o cenário do Focus vira sensibilidade setorial.

## 2. Princípios do módulo Ativos

1. **Uso pessoal, metodologia aberta.** Toda nota, faixa ou carteira mostra a fórmula,
   as premissas e a decomposição. Nada de caixa-preta.
2. **Score, não ordem.** A linguagem é quantitativa ("score", "faixa estimada",
   "margem de segurança calculada"). O guardrail `ativos/core/linguagem.py` bloqueia
   verbos de ordem e "preço-alvo" em qualquer texto exibido.
3. **Faixa, nunca número único.** O valor intrínseco é uma faixa entre modelos
   aplicáveis. Modelo inaplicável aparece como "não se aplica".
4. **Sem olhar o futuro.** Balanço só entra na data de entrega à CVM (`DT_RECEB`).
   Todo backtest é point-in-time.
5. **Dado incompleto não vira nota.** Cobertura abaixo de 70% aparece como "não
   avaliado".
6. **Fontes oficiais e gratuitas.** CVM Dados Abertos, B3 COTAHIST, BACEN e Tesouro.
   Exceção só por decisão registrada, como a tabela curada de ETFs.
7. **Fronteira regulatória.** O módulo é ferramenta de uso próprio. Abrir para
   terceiros esbarra nas regras da CVM para analista e consultor de valores mobiliários
   (Res. 19 e 20/2021) e exige validação jurídica antes. Este documento não é parecer
   legal.

## 3. Arquitetura

```
focuslens/   módulo Macro (sem mudança de contrato)
ativos/
  adapters/  CVM (DFP, ITR, FCA, cadastro, FII, fundos), B3 COTAHIST, armazém Parquet
  core/      modelo point-in-time, métricas, valuation, score, screener, risco, otimizador, backtest
  ui/        páginas Streamlit do módulo
app_financas.py   entrada com st.navigation: Macro e Ativos
```

- **Bruto:** fica em `%USERPROFILE%\.cache\lastro\raw`, fora do OneDrive e do git.
- **Derivado:** tabelas em Parquet geradas por workflow diário e publicadas como asset
  de release.
- **Mobile:** fica de fora até a Fase 7. Quando entrar, ganha um contrato próprio
  `ativos-v1`, e o snapshot `v1` do FocusLens não muda.

## 4. Fases

| Fase | Entrega | Gate | Situação |
|---|---|---|---|
| 0 | Navegação Macro + Ativos, este plano, [relatório de cobertura](../validation/COBERTURA_ATIVOS_FASE0.md) | relatório revisado pelo Raul | concluída em 2026-10-09 |
| 1 | Base de dados point-in-time: adapters, normalização (escala, contas, units) e pipeline local | testes com fixtures sintéticas e pipeline real | concluída em 2026-10-09; automação/asset pendentes |
| 2 | Métricas (ações e FIIs), ficha do ativo e screener com presets | golden tests calculados à mão | concluída em 2026-10-09 |
| 3 | ETFs: tabela curada, exposição, ranking por custo, liquidez, PL e tracking | conferência de 10 ETFs | próxima |
| 4 | Valor estimado em faixa (Graham, Bazin, Gordon, múltiplo setorial e FIIs); DCF 2 estágios | golden tests e sensibilidade | parcial em 2026-10-09; DCF pendente |
| 5 | Score Lastro (6 fatores, percentil setorial, pesos editáveis) e Score Lab (backtest por quintil, IC) | teste anti look-ahead | próxima |
| 6 | Risco, otimizador (mínima variância, MV com Ledoit-Wolf, HRP), fronteira, walk-forward, raio-x da carteira importada | testes numéricos de restrição e determinismo | planejada |
| 7 | Proventos e fatos relevantes (CVM IPE), renda passiva, mobile | conforme item | planejada |

O detalhamento de métricas, modelos e fatores aprovado em 2026-10-09 está resumido
abaixo e é refinado no início de cada fase.

## 5. Métricas, modelos e fatores

**Ações** (TTM a partir de DFP + ITR; setor financeiro com conjunto próprio):

| Grupo | Métricas |
|---|---|
| Valor | P/L, P/VP, EV/EBIT, EV/EBITDA, earnings yield |
| Qualidade | ROE, ROIC, margens, Piotroski F-score |
| Saúde | dívida líquida/EBITDA, liquidez corrente, Altman Z |
| Crescimento | CAGR de receita e lucro em 3 e 5 anos, consistência de lucro |
| Dividendos | DY 12m, payout, anos consecutivos pagando |

**FIIs:** P/VP, DY 12m, liquidez, cotistas, segmento (classificado pela composição do
ativo), vacância, concentração e prêmio sobre a NTN-B.

**ETFs:** agrupamento por exposição e ranking por taxa, liquidez, PL e tracking
difference.

**Valor intrínseco:**
- Modelos:
  - Graham: √(22,5 × LPA × VPA);
  - Bazin com taxa mínima editável, padrão de 6%;
  - Gordon com `k = Tesouro Prefixado de 5 anos + ERP` e crescimento editável;
  - múltiplos setoriais sobre empresas distintas, excluindo o próprio CNPJ;
  - FII patrimonial e renda de 12 meses capitalizada pela taxa prefixada líquida de 15%;
  - DCF de 2 estágios, com WACC derivado da curva Tesouro e beta do COTAHIST, pendente.
- Saída: faixa P25–P75, mediana, quantidade de modelos, margem calculada e posição do
  preço na faixa; menos de dois modelos permanece sem faixa.
- Premissas são visíveis, editáveis e compartilhadas entre as duas buscas e a ficha.
  O parquet esquema 3 persiste apenas os insumos; o valuation é recalculado na sessão.

**Score Lastro (0–100, letras A–E por quintil):**
- Fatores: Valor, Qualidade, Saúde, Crescimento, Dividendos e Risco.
- Cada fator é a média de percentis setoriais winsorizados.
- Perfis de peso: Equilibrado, Qualidade, Valor e Dividendos, além de pesos livres.

**Carteira:**
- Métricas: volatilidade, beta, drawdown máximo, Sharpe e Sortino (vs. CDI), correlação
  média, razão de diversificação e HHI.
- Otimizadores: pesos iguais, mínima variância, média-variância com Ledoit-Wolf e HRP.
- Restrições por ativo, setor e classe.

## 6. Decisões em aberto

- **Retorno total para backtest:** aproximação oficial pela DVA ou série ajustada do
  Yahoo. Ver o relatório de cobertura.
- **Próximo modelo de valor:** definir fluxo de caixa, beta, dívida e crescimento do
  DCF de dois estágios antes de implementar, sem preencher lacunas com estimativas opacas.
- **Nome definitivo** da plataforma.
