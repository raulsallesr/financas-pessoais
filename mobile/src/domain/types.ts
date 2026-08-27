export type AssetClass =
  | "Renda fixa pós-fixada"
  | "Renda fixa prefixada"
  | "Títulos IPCA+"
  | "Fundos imobiliários / FIAGRO"
  | "Bolsa brasileira"
  | "Exterior / dólar";

export type SignalTone = "positive" | "attention" | "neutral";

export type ClassEffect = {
  tone: SignalTone;
  headline: string;
  explanation: string;
};

export type MarketSignal = {
  id: string;
  label: string;
  value: string;
  change: string;
  headline: string;
  explanation: string;
  source: string;
  updatedAt: string;
  tone: SignalTone;
  effects: Partial<Record<AssetClass, ClassEffect>>;
};

export type Position = {
  id: string;
  name: string;
  shortName: string;
  assetClass: AssetClass;
  amount: number;
};

export type MarketSnapshot = {
  mode: "demo";
  asOf: string;
  verdict: string;
  verdictSupport: string;
  sourcesAvailable: number;
  sourcesTotal: number;
  signals: readonly MarketSignal[];
  positions: readonly Position[];
};

export type PortfolioImpact = {
  position: Position;
  effect: ClassEffect;
  allocationPercent: number;
};

export type RateScenario = {
  shockBps: number;
  title: string;
  explanation: string;
  impacts: readonly PortfolioImpact[];
};
