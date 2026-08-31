import { render, screen, userEvent } from "@testing-library/react-native";

import { demoSnapshot } from "../../src/data/demoSnapshot";
import { createMoneyLabSession } from "../../src/components/MoneyLabPanel";
import { ScenariosScreen } from "../../src/screens/ScenariosScreen";
import testIds from "../../src/testing/testIds.json";

describe("ScenariosScreen", () => {
  test("mantém aporte e sensibilidade como hipóteses separadas", async () => {
    const onShockChange = jest.fn();
    const user = userEvent.setup();
    await render(
      <ScenariosScreen
        hideAmounts={false}
        moneyLabSession={createMoneyLabSession()}
        onMoneyLabSessionChange={jest.fn()}
        onShockChange={onShockChange}
        onToggleAmounts={jest.fn()}
        portfolioMode="demo"
        shockBps={50}
        snapshot={demoSnapshot}
      />,
    );

    expect(screen.getByTestId(testIds.screens.scenarios)).toBeTruthy();
    expect(screen.getByText("Brinque com números antes de olhar produtos")).toBeTruthy();
    expect(screen.getByText("E se eu aportar nesta classe?")).toBeTruthy();
    expect(screen.getByText("E se os juros mudarem?")).toBeTruthy();

    await user.press(
      screen.getByLabelText("Aplicar choque de −50 pontos-base"),
    );

    expect(onShockChange).toHaveBeenCalledWith(-50);
    expect(screen.queryByTestId(testIds.contribution.result)).toBeNull();
  });

  test("retorna à revisão sem preencher uma hipótese nova", async () => {
    const onReturn = jest.fn();
    const onShockChange = jest.fn();
    const user = userEvent.setup();
    await render(
      <ScenariosScreen
        hideAmounts={false}
        moneyLabSession={createMoneyLabSession()}
        onMoneyLabSessionChange={jest.fn()}
        onShockChange={onShockChange}
        onToggleAmounts={jest.fn()}
        portfolioMode="demo"
        reviewContext={{
          signalLabel: "Curva prefixada",
          onReturn,
        }}
        shockBps={50}
        snapshot={demoSnapshot}
      />,
    );

    expect(
      screen.getByText(
        "A revisão não mudou valor, classe ou choque. Explore uma hipótese por conta própria e volte para fechar com o limite da leitura.",
      ),
    ).toBeTruthy();
    expect(onShockChange).not.toHaveBeenCalled();

    await user.press(
      screen.getByTestId(testIds.weeklyReview.returnFromScenarios),
    );
    expect(onReturn).toHaveBeenCalledTimes(1);
    expect(onShockChange).not.toHaveBeenCalled();
  });
});
