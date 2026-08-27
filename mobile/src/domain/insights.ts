import {
  AssetClass,
  ClassEffect,
  MarketSnapshot,
  PortfolioImpact,
  RateScenario,
  SignalTone,
} from "./types";

export const ALL_CLASSES = "Todos" as const;
export type ClassFilter = typeof ALL_CLASSES | AssetClass;

export function portfolioTotal(snapshot: MarketSnapshot): number {
  return snapshot.positions.reduce((total, position) => total + position.amount, 0);
}

export function allocationPercent(
  snapshot: MarketSnapshot,
  amount: number,
): number {
  const total = portfolioTotal(snapshot);
  return total > 0 ? (amount / total) * 100 : 0;
}

export function availableClasses(snapshot: MarketSnapshot): readonly AssetClass[] {
  return [...new Set(snapshot.positions.map((position) => position.assetClass))];
}

export function signalById(snapshot: MarketSnapshot, signalId: string) {
  const signal = snapshot.signals.find((item) => item.id === signalId);
  if (!signal) {
    throw new Error(`Sinal não encontrado: ${signalId}`);
  }
  return signal;
}

export function impactsForSignal(
  snapshot: MarketSnapshot,
  signalId: string,
  classFilter: ClassFilter = ALL_CLASSES,
): readonly PortfolioImpact[] {
  const signal = signalById(snapshot, signalId);
  return snapshot.positions
    .filter(
      (position) =>
        classFilter === ALL_CLASSES || position.assetClass === classFilter,
    )
    .flatMap((position) => {
      const effect = signal.effects[position.assetClass];
      if (!effect) {
        return [];
      }
      return [
        {
          position,
          effect,
          allocationPercent: allocationPercent(snapshot, position.amount),
        },
      ];
    })
    .sort((left, right) => right.position.amount - left.position.amount);
}

export function impactedAllocation(impacts: readonly PortfolioImpact[]): number {
  return impacts.reduce((total, impact) => total + impact.allocationPercent, 0);
}

function scenarioEffect(
  assetClass: AssetClass,
  shockBps: number,
): ClassEffect | null {
  if (shockBps === 0) {
    return null;
  }

  const ratesRise = shockBps > 0;
  const matrix: Partial<
    Record<AssetClass, { rising: ClassEffect; falling: ClassEffect }>
  > = {
    "Renda fixa pós-fixada": {
      rising: {
        tone: "positive",
        headline: "Carrego tende a ganhar força",
        explanation:
          "Taxas mais altas costumam elevar gradualmente a remuneração pós-fixada.",
      },
      falling: {
        tone: "attention",
        headline: "Carrego tende a perder força",
        explanation:
          "Taxas menores costumam reduzir gradualmente a remuneração pós-fixada.",
      },
    },
    "Renda fixa prefixada": {
      rising: {
        tone: "attention",
        headline: "Preço fica mais sensível",
        explanation:
          "Uma alta das taxas tende a pressionar o preço de títulos prefixados antes do vencimento.",
      },
      falling: {
        tone: "positive",
        headline: "Preço tende a respirar",
        explanation:
          "Uma queda das taxas tende a favorecer o preço de títulos prefixados antes do vencimento.",
      },
    },
    "Títulos IPCA+": {
      rising: {
        tone: "attention",
        headline: "Marcação a mercado mais exigente",
        explanation:
          "Juros reais maiores podem pressionar preços no curto prazo, apesar da correção pelo IPCA.",
      },
      falling: {
        tone: "positive",
        headline: "Marcação a mercado mais favorável",
        explanation:
          "Juros reais menores podem aliviar os preços, sem eliminar o risco de oscilação.",
      },
    },
    "Fundos imobiliários / FIAGRO": {
      rising: {
        tone: "attention",
        headline: "Prêmio relativo mais apertado",
        explanation:
          "Taxas maiores elevam a comparação com renda fixa e podem pressionar avaliações.",
      },
      falling: {
        tone: "positive",
        headline: "Prêmio relativo ganha espaço",
        explanation:
          "Taxas menores podem aliviar a comparação com renda fixa, ainda com riscos próprios do fundo.",
      },
    },
  };
  const pair = matrix[assetClass];
  return pair ? (ratesRise ? pair.rising : pair.falling) : null;
}

export function buildRateScenario(
  snapshot: MarketSnapshot,
  shockBps: number,
): RateScenario {
  if (!Number.isInteger(shockBps) || shockBps < -100 || shockBps > 100) {
    throw new Error("O choque deve ser um inteiro entre -100 e 100 bps.");
  }
  const impacts = snapshot.positions.flatMap((position) => {
    const effect = scenarioEffect(position.assetClass, shockBps);
    if (!effect) {
      return [];
    }
    return [
      {
        position,
        effect,
        allocationPercent: allocationPercent(snapshot, position.amount),
      },
    ];
  });
  const direction = shockBps > 0 ? "subirem" : shockBps < 0 ? "caírem" : "não mudarem";
  return {
    shockBps,
    title:
      shockBps === 0
        ? "Fotografia observada"
        : `Se as taxas ${direction} ${Math.abs(shockBps)} bps`,
    explanation:
      shockBps === 0
        ? "Nenhum movimento foi aplicado. Use os controles para explorar sensibilidades."
        : "É uma sensibilidade educacional, não uma previsão de retorno nem uma recomendação.",
    impacts,
  };
}

export function toneLabel(tone: SignalTone): string {
  return {
    positive: "Pode favorecer",
    attention: "Pede atenção",
    neutral: "Efeito misto",
  }[tone];
}
