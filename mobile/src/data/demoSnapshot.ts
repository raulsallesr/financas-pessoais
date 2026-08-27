import { MarketSnapshot } from "../domain/types";

export const demoSnapshot: MarketSnapshot = {
  mode: "demo",
  asOf: "26 ago 2026",
  verdict: "A curva ficou mais benigna que o Focus",
  verdictSupport:
    "As expectativas seguem firmes, mas os prefixados recuaram em cinco vencimentos.",
  sourcesAvailable: 2,
  sourcesTotal: 2,
  signals: [
    {
      id: "curva",
      label: "Curva prefixada",
      value: "−24 bps",
      change: "mediana em 5 vencimentos",
      headline: "O mercado aliviou parte do prêmio",
      explanation:
        "As taxas prefixadas recuaram na fotografia recente, com movimento mais forte na ponta longa.",
      source: "Tesouro Transparente",
      updatedAt: "26 ago 2026",
      tone: "positive",
      effects: {
        "Renda fixa prefixada": {
          tone: "positive",
          headline: "Marcação a mercado respira",
          explanation:
            "Taxas menores tendem a favorecer o preço antes do vencimento; a taxa contratada continua valendo no carrego até o fim.",
        },
        "Títulos IPCA+": {
          tone: "positive",
          headline: "Juros longos dão algum alívio",
          explanation:
            "A direção ajuda a leitura de duration, mas não substitui a curva real dos títulos IPCA+.",
        },
        "Fundos imobiliários / FIAGRO": {
          tone: "positive",
          headline: "Comparação com renda fixa melhora",
          explanation:
            "O recuo das taxas pode aliviar o prêmio relativo, sem remover risco de crédito, vacância ou gestão.",
        },
      },
    },
    {
      id: "focus",
      label: "Focus · Selic",
      value: "13,75%",
      change: "sem revisão na semana",
      headline: "Expectativa de Selic segue firme",
      explanation:
        "A mediana do Focus não mudou entre as duas últimas fotografias comparáveis.",
      source: "BACEN · Focus",
      updatedAt: "21 ago 2026",
      tone: "neutral",
      effects: {
        "Renda fixa pós-fixada": {
          tone: "positive",
          headline: "Carrego continua relevante",
          explanation:
            "Uma Selic esperada elevada mantém o pós-fixado sensível ao nível dos juros no curto prazo.",
        },
        "Renda fixa prefixada": {
          tone: "attention",
          headline: "Taxa contratada exige horizonte",
          explanation:
            "Juros altos por mais tempo podem manter a oscilação de preço antes do vencimento.",
        },
        "Bolsa brasileira": {
          tone: "attention",
          headline: "Custo de capital segue no radar",
          explanation:
            "Juros altos podem pressionar avaliações, mas empresas e setores respondem de formas diferentes.",
        },
      },
    },
    {
      id: "inflacao",
      label: "Focus · IPCA",
      value: "4,20%",
      change: "−0,05 p.p. em 4 semanas",
      headline: "Inflação esperada perdeu um pouco de força",
      explanation:
        "A direção é benigna, mas a mediana ainda precisa ser lida com horizonte e dispersão.",
      source: "BACEN · Focus",
      updatedAt: "21 ago 2026",
      tone: "positive",
      effects: {
        "Títulos IPCA+": {
          tone: "neutral",
          headline: "Proteção e preço contam histórias diferentes",
          explanation:
            "A correção pelo IPCA permanece, enquanto o preço também responde à taxa real negociada.",
        },
        "Renda fixa prefixada": {
          tone: "positive",
          headline: "Inflação menor ajuda a leitura nominal",
          explanation:
            "Uma expectativa menor pode aliviar prêmio nominal, sem garantir queda das taxas.",
        },
      },
    },
    {
      id: "dolar",
      label: "Dólar PTAX",
      value: "+2,4%",
      change: "em 30 dias",
      headline: "O dólar ganhou força no período",
      explanation:
        "A variação amplia a diferença entre exposições locais e ativos ligados ao exterior.",
      source: "PTAX · BACEN",
      updatedAt: "26 ago 2026",
      tone: "attention",
      effects: {
        "Exterior / dólar": {
          tone: "positive",
          headline: "Câmbio reforça a exposição em reais",
          explanation:
            "A alta do dólar eleva o valor em reais, separadamente do desempenho do ativo no exterior.",
        },
        "Bolsa brasileira": {
          tone: "neutral",
          headline: "Efeito depende do negócio",
          explanation:
            "Exportadoras e importadoras podem reagir de forma diferente; o índice agregado esconde essa dispersão.",
        },
      },
    },
  ],
  positions: [
    {
      id: "pos-1",
      name: "Tesouro Selic 2029",
      shortName: "Selic 2029",
      assetClass: "Renda fixa pós-fixada",
      amount: 28000,
    },
    {
      id: "pos-2",
      name: "Tesouro Prefixado 2029",
      shortName: "Prefixado 2029",
      assetClass: "Renda fixa prefixada",
      amount: 18500,
    },
    {
      id: "pos-3",
      name: "ETF de bolsa brasileira",
      shortName: "Bolsa Brasil",
      assetClass: "Bolsa brasileira",
      amount: 12000,
    },
    {
      id: "pos-4",
      name: "Fundo imobiliário de papel",
      shortName: "FII de papel",
      assetClass: "Fundos imobiliários / FIAGRO",
      amount: 8000,
    },
    {
      id: "pos-5",
      name: "ETF de ações globais",
      shortName: "Ações globais",
      assetClass: "Exterior / dólar",
      amount: 6000,
    },
  ],
};
