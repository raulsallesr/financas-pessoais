import { allocationByClass, portfolioTotal } from "./insights";
import { ASSET_CLASSES, MAX_POSITION_AMOUNT } from "./privatePortfolio";
import { AssetClass, MarketSnapshot } from "./types";

export type ContributionAllocation = {
  assetClass: AssetClass;
  amountBefore: number;
  amountAfter: number;
  allocationBeforePercent: number;
  allocationAfterPercent: number;
  deltaPercentagePoints: number;
  receivesContribution: boolean;
};

export type ContributionSimulation = {
  contributionAmount: number;
  targetClass: AssetClass;
  portfolioBefore: number;
  portfolioAfter: number;
  allocations: readonly ContributionAllocation[];
};

export function simulateClassContribution(
  snapshot: MarketSnapshot,
  contributionAmount: number,
  targetClass: AssetClass,
): ContributionSimulation {
  if (
    !Number.isFinite(contributionAmount) ||
    contributionAmount <= 0 ||
    contributionAmount > MAX_POSITION_AMOUNT
  ) {
    throw new Error("O aporte hipotético deve ser um valor positivo válido.");
  }
  if (!ASSET_CLASSES.includes(targetClass)) {
    throw new Error("A classe escolhida não faz parte do contrato do app.");
  }

  const portfolioBefore = portfolioTotal(snapshot);
  const portfolioAfter = portfolioBefore + contributionAmount;
  const currentAmounts = new Map(
    allocationByClass(snapshot).map((item) => [item.assetClass, item.amount]),
  );

  const allocations = ASSET_CLASSES.flatMap((assetClass) => {
    const amountBefore = currentAmounts.get(assetClass) ?? 0;
    const receivesContribution = assetClass === targetClass;
    const amountAfter =
      amountBefore + (receivesContribution ? contributionAmount : 0);
    if (amountAfter === 0) {
      return [];
    }

    const allocationBeforePercent =
      portfolioBefore > 0 ? (amountBefore / portfolioBefore) * 100 : 0;
    const allocationAfterPercent = (amountAfter / portfolioAfter) * 100;
    return [
      {
        assetClass,
        amountBefore,
        amountAfter,
        allocationBeforePercent,
        allocationAfterPercent,
        deltaPercentagePoints:
          allocationAfterPercent - allocationBeforePercent,
        receivesContribution,
      },
    ];
  }).sort((left, right) => {
    if (left.amountAfter !== right.amountAfter) {
      return right.amountAfter - left.amountAfter;
    }
    return (
      ASSET_CLASSES.indexOf(left.assetClass) -
      ASSET_CLASSES.indexOf(right.assetClass)
    );
  });

  return {
    contributionAmount,
    targetClass,
    portfolioBefore,
    portfolioAfter,
    allocations,
  };
}
