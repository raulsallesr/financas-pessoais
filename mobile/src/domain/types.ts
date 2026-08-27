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

export type MarketSource = {
  id: string;
  label: string;
  available: boolean;
  asOf: string | null;
  status: string;
};

export type SnapshotProof = {
  source: string;
  text: string;
};

export type Position = {
  id: string;
  name: string;
  shortName: string;
  assetClass: AssetClass;
  amount: number;
};

export type MarketSnapshot = {
  schemaVersion: 1;
  mode: "demo" | "live";
  generatedAt: string;
  asOf: string;
  verdict: string;
  verdictSupport: string;
  proofs: readonly SnapshotProof[];
  sources: readonly MarketSource[];
  sourcesAvailable: number;
  sourcesTotal: number;
  limits: readonly string[];
  changeConditions: readonly string[];
  signals: readonly MarketSignal[];
  positions: readonly Position[];
  fallbackReason?: string;
};

export type PublicMarketSnapshotV1 = Omit<
  MarketSnapshot,
  "mode" | "positions" | "sourcesAvailable" | "sourcesTotal" | "fallbackReason"
> & {
  mode: "live";
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
