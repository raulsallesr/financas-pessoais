import { useState } from "react";
import { render, screen, userEvent } from "@testing-library/react-native";

import {
  WeeklyReviewPanel,
  WeeklyReviewStep,
} from "../../src/components/WeeklyReviewPanel";
import { demoSnapshot } from "../../src/data/demoSnapshot";
import { createPublicSnapshotHistory } from "../../src/domain/snapshotHistory";
import {
  MarketSnapshot,
  PublicMarketSnapshotV1,
} from "../../src/domain/types";
import testIds from "../../src/testing/testIds.json";

function publicSnapshot(
  snapshot: MarketSnapshot,
  generatedAt: string,
  asOf: string,
): PublicMarketSnapshotV1 {
  const {
    fallbackReason: _fallbackReason,
    positions: _positions,
    sourcesAvailable: _sourcesAvailable,
    sourcesTotal: _sourcesTotal,
    ...publicFields
  } = snapshot;
  return {
    ...publicFields,
    mode: "live",
    generatedAt,
    asOf,
  };
}

function StatefulReview({
  onExploreScenarios,
  onFinish,
}: {
  onExploreScenarios: () => void;
  onFinish: () => void;
}) {
  const [step, setStep] = useState<WeeklyReviewStep>(0);
  const previous = publicSnapshot(
    {
      ...demoSnapshot,
      signals: demoSnapshot.signals.map((signal) =>
        signal.id === "curva"
          ? { ...signal, value: "−12 bps", change: "mediana anterior" }
          : signal,
      ),
    },
    "2026-08-19T12:00:00Z",
    "2026-08-19",
  );
  const current = publicSnapshot(
    demoSnapshot,
    "2026-08-26T12:00:00Z",
    "2026-08-26",
  );

  return (
    <WeeklyReviewPanel
      favorite
      history={createPublicSnapshotHistory([current, previous])}
      onCancel={jest.fn()}
      onExploreScenarios={onExploreScenarios}
      onFinish={onFinish}
      onStepChange={setStep}
      signalId="curva"
      snapshot={demoSnapshot}
      step={step}
    />
  );
}

describe("WeeklyReviewPanel", () => {
  test("percorre mudança, prova, carteira, Cenários e limite sem escolher hipótese", async () => {
    const onExploreScenarios = jest.fn();
    const onFinish = jest.fn();
    const user = userEvent.setup();
    await render(
      <StatefulReview
        onExploreScenarios={onExploreScenarios}
        onFinish={onFinish}
      />,
    );

    expect(screen.getByText("O histórico registrou uma mudança literal")).toBeTruthy();
    expect(screen.getByText("Acompanhando")).toBeTruthy();

    await user.press(screen.getByTestId(testIds.weeklyReview.next));
    expect(screen.getByText("Número, movimento, fonte e data")).toBeTruthy();
    expect(screen.getByText("Curva de juros")).toBeTruthy();

    await user.press(screen.getByTestId(testIds.weeklyReview.next));
    expect(screen.getByText("2 posições relacionadas")).toBeTruthy();
    expect(screen.getByText("Prefixado 2029")).toBeTruthy();

    await user.press(screen.getByTestId(testIds.weeklyReview.next));
    expect(screen.getByText("Escolha você mesmo uma hipótese")).toBeTruthy();
    await user.press(
      screen.getByTestId(testIds.weeklyReview.exploreScenarios),
    );
    expect(onExploreScenarios).toHaveBeenCalledTimes(1);

    await user.press(
      screen.getByLabelText("Continuar para o limite sem abrir Cenários"),
    );
    expect(screen.getByText("A leitura termina no próprio limite")).toBeTruthy();
    await user.press(screen.getByTestId(testIds.weeklyReview.finish));
    expect(onFinish).toHaveBeenCalledTimes(1);
  });

  test("explica o estado sem histórico comparável", async () => {
    await render(
      <WeeklyReviewPanel
        favorite={false}
        history={null}
        onCancel={jest.fn()}
        onExploreScenarios={jest.fn()}
        onFinish={jest.fn()}
        onStepChange={jest.fn()}
        signalId="focus"
        snapshot={demoSnapshot}
        step={0}
      />,
    );

    expect(screen.getByText("Ainda sem duas fotografias comparáveis")).toBeTruthy();
    expect(
      screen.getByText(/Quando houver outra fotografia pública compatível/),
    ).toBeTruthy();
  });

  test("preserva a ausência de efeito sem inventar posição ou impacto", async () => {
    const snapshotWithoutEffect: MarketSnapshot = {
      ...demoSnapshot,
      signals: demoSnapshot.signals.map((signal) =>
        signal.id === "curva" ? { ...signal, effects: {} } : signal,
      ),
    };
    await render(
      <WeeklyReviewPanel
        favorite={false}
        history={null}
        onCancel={jest.fn()}
        onExploreScenarios={jest.fn()}
        onFinish={jest.fn()}
        onStepChange={jest.fn()}
        signalId="curva"
        snapshot={snapshotWithoutEffect}
        step={2}
      />,
    );

    expect(
      screen.getByText("Sem efeito classificado para este recorte"),
    ).toBeTruthy();
    expect(
      screen.getByText(/Sem relação declarada continua sem relação/),
    ).toBeTruthy();
    expect(screen.queryByText("Prefixado 2029")).toBeNull();
  });
});
