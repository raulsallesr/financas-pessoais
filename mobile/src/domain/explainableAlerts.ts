import { impactedAllocation, impactsForSignal, signalById } from "./insights";
import { AssetClass, MarketSnapshot, MarketSignal } from "./types";

export type ExplainableAlert = {
  signal: MarketSignal;
  whatChanged: string;
  whatProves: string;
  whereItAffects: string;
  whatItDoesNotProve: string;
  affectedClasses: readonly AssetClass[];
  affectedPositionCount: number;
  affectedAllocationPercent: number;
};

export function buildExplainableAlert(
  snapshot: MarketSnapshot,
  signalId: string,
): ExplainableAlert {
  const signal = signalById(snapshot, signalId);
  const impacts = impactsForSignal(snapshot, signalId);
  const affectedClasses = [
    ...new Set(impacts.map((impact) => impact.position.assetClass)),
  ];
  const affectedAllocationPercent = impactedAllocation(impacts);
  const whereItAffects = impacts.length
    ? `${impacts.length} ${impacts.length === 1 ? "posição" : "posições"} em ${affectedClasses.join(", ")}, equivalentes a ${affectedAllocationPercent.toFixed(0)}% do recorte atual.`
    : snapshot.positions.length
      ? "Nenhuma relação direta foi classificada entre este sinal e as classes da carteira atual."
      : "Ainda não existe carteira para cruzar com este sinal público.";
  const firstLimit = snapshot.limits[0]
    ? ` Limite registrado: ${snapshot.limits[0]}`
    : "";

  return {
    signal,
    whatChanged: `${signal.headline}. ${signal.explanation}`,
    whatProves: `${signal.label}: ${signal.value}; ${signal.change}. Fonte: ${signal.source}, fotografia de ${signal.updatedAt}.`,
    whereItAffects,
    whatItDoesNotProve:
      `Não prova retorno futuro, causalidade nem recomendação de compra ou venda.${firstLimit}`,
    affectedClasses,
    affectedPositionCount: impacts.length,
    affectedAllocationPercent,
  };
}
