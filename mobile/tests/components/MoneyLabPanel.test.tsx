import { useState } from "react";
import {
  fireEvent,
  render,
  screen,
  userEvent,
  waitFor,
} from "@testing-library/react-native";

import {
  createMoneyLabSession,
  MoneyLabPanel,
  MoneyLabSession,
} from "../../src/components/MoneyLabPanel";
import testIds from "../../src/testing/testIds.json";

function Harness({
  hideAmounts = false,
  initialSession,
}: {
  hideAmounts?: boolean;
  initialSession?: MoneyLabSession;
}) {
  const [session, setSession] = useState<MoneyLabSession>(
    () => initialSession ?? createMoneyLabSession(),
  );
  return (
    <MoneyLabPanel
      hideAmounts={hideAmounts}
      onSessionChange={setSession}
      session={session}
    />
  );
}

describe("MoneyLabPanel", () => {
  test("começa por um exemplo editável e separa aporte de juros", async () => {
    await render(<Harness />);

    expect(screen.getByTestId(testIds.moneyLab.panel)).toBeTruthy();
    expect(screen.getAllByRole("radio")).toHaveLength(5);
    expect(
      screen.getByTestId(testIds.moneyLab.tools.growth).props.accessibilityState,
    ).toEqual({ selected: true });
    expect(screen.getByTestId(testIds.moneyLab.result)).toBeTruthy();
    expect(screen.getAllByText("Colocado por você").length).toBeGreaterThan(1);
    expect(screen.getAllByText("Juros do cenário").length).toBeGreaterThan(1);
    expect(
      screen.getByText(
        "A taxa foi mantida constante só para a matemática funcionar. O resultado não prevê mercado, imposto, taxa de produto ou poder de compra quando a inflação estiver desligada.",
      ),
    ).toBeTruthy();
  });

  test("revela inflação somente quando a pessoa pedir", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    expect(screen.queryByTestId(testIds.moneyLab.inflationInput)).toBeNull();
    await user.press(screen.getByTestId(testIds.moneyLab.inflationToggle));

    expect(screen.getByTestId(testIds.moneyLab.inflationInput)).toBeTruthy();
    expect(screen.getByText("Em dinheiro de hoje")).toBeTruthy();
  });

  test("percorre meta, espera e hábito sem misturar as perguntas", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.tools.goal));
    expect(
      screen.getByText("Quanto eu precisaria guardar por mês?"),
    ).toBeTruthy();
    expect(screen.getByText("APORTE MENSAL DO CENÁRIO")).toBeTruthy();

    await user.press(screen.getByTestId(testIds.moneyLab.tools.delay));
    expect(screen.getByText("E se eu começar mais tarde?")).toBeTruthy();
    expect(screen.getByText("DIFERENÇA NO FIM")).toBeTruthy();

    await user.press(screen.getByTestId(testIds.moneyLab.tools.habit));
    expect(
      screen.getByText("Quanto uma recorrência representa no tempo?"),
    ).toBeTruthy();
    expect(screen.getByText("EQUIVALENTE MÉDIO POR MÊS")).toBeTruthy();
  });

  test("pede um palpite antes de revelar o desafio", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.tools.challenge));
    expect(
      screen.queryByTestId(testIds.moneyLab.challengeResult),
    ).toBeNull();

    await user.press(screen.getByTestId(testIds.moneyLab.guessRate));

    expect(screen.getByTestId(testIds.moneyLab.challengeResult)).toBeTruthy();
    expect(screen.getByText("NESTE CENÁRIO, PESOU MAIS")).toBeTruthy();
    expect(
      screen.getByText(
        "Seu palpite foi diferente do resultado — e essa é a graça do teste.",
      ),
    ).toBeTruthy();
  });

  test("descarta o resultado quando os dois valores monetários ficam zerados", async () => {
    const invalidSession = {
      ...createMoneyLabSession(),
      initialAmountText: "0",
      monthlyContributionText: "0",
    };
    await render(<Harness initialSession={invalidSession} />);

    const initial = screen.getByTestId(testIds.moneyLab.initialInput);
    const monthly = screen.getByTestId(testIds.moneyLab.monthlyInput);

    expect(screen.queryByTestId(testIds.moneyLab.result)).toBeNull();
    expect(
      screen.queryByText("Informe um valor inicial ou um aporte mensal."),
    ).toBeNull();

    await fireEvent(initial, "blur");
    await fireEvent(monthly, "blur");

    await waitFor(() =>
      expect(
        screen.getAllByText("Informe um valor inicial ou um aporte mensal."),
      ).toHaveLength(2),
    );
  });

  test("modo discreto mascara entradas e resultados monetários", async () => {
    await render(<Harness hideAmounts />);

    expect(
      screen.getByText(
        "Modo discreto ativo: entradas e resultados monetários estão ocultos.",
      ),
    ).toBeTruthy();
    expect(
      screen.getByTestId(testIds.moneyLab.initialInput).props.secureTextEntry,
    ).toBe(true);
    expect(
      screen.getByTestId(testIds.moneyLab.monthlyInput).props.secureTextEntry,
    ).toBe(true);
    expect(screen.getAllByText("R$ ••••••").length).toBeGreaterThanOrEqual(2);
  });
});
