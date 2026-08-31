import { render, screen, userEvent } from "@testing-library/react-native";

import { demoSnapshot } from "../../src/data/demoSnapshot";
import { ScenariosScreen } from "../../src/screens/ScenariosScreen";
import testIds from "../../src/testing/testIds.json";

describe("ScenariosScreen", () => {
  test("mantém aporte e sensibilidade como hipóteses separadas", async () => {
    const onShockChange = jest.fn();
    const user = userEvent.setup();
    await render(
      <ScenariosScreen
        hideAmounts={false}
        onShockChange={onShockChange}
        onToggleAmounts={jest.fn()}
        portfolioMode="demo"
        shockBps={50}
        snapshot={demoSnapshot}
      />,
    );

    expect(screen.getByTestId(testIds.screens.scenarios)).toBeTruthy();
    expect(screen.getByText("E se eu aportar nesta classe?")).toBeTruthy();
    expect(screen.getByText("E se os juros mudarem?")).toBeTruthy();

    await user.press(
      screen.getByLabelText("Aplicar choque de −50 pontos-base"),
    );

    expect(onShockChange).toHaveBeenCalledWith(-50);
    expect(screen.queryByTestId(testIds.contribution.result)).toBeNull();
  });
});
