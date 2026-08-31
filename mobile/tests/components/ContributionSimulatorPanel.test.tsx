import {
  render,
  screen,
  userEvent,
} from "@testing-library/react-native";

import { ContributionSimulatorPanel } from "../../src/components/ContributionSimulatorPanel";
import { demoSnapshot } from "../../src/data/demoSnapshot";
import testIds from "../../src/testing/testIds.json";

describe("ContributionSimulatorPanel", () => {
  test("começa sem hipótese implícita e valida os dois campos", async () => {
    const user = userEvent.setup();
    await render(
      <ContributionSimulatorPanel hideAmounts={false} snapshot={demoSnapshot} />,
    );

    expect(screen.queryByTestId(testIds.contribution.result)).toBeNull();
    expect(screen.getAllByRole("radio")).toHaveLength(6);
    for (const option of screen.getAllByRole("radio")) {
      expect(option.props.accessibilityState).toEqual({ selected: false });
    }

    await user.press(screen.getByTestId(testIds.contribution.submit));

    expect(
      screen.getByText("Informe um valor positivo, por exemplo 1.250,50."),
    ).toBeTruthy();
    expect(
      screen.getByText("Escolha a classe que receberia o aporte."),
    ).toBeTruthy();
  });

  test("compara antes e depois e descarta um resultado que ficou obsoleto", async () => {
    const user = userEvent.setup();
    await render(
      <ContributionSimulatorPanel hideAmounts={false} snapshot={demoSnapshot} />,
    );

    const amountInput = screen.getByTestId(testIds.contribution.amountInput);
    await user.type(amountInput, "10000");
    await user.press(
      screen.getByTestId(testIds.contribution.classes.inflationLinked),
    );
    await user.press(screen.getByTestId(testIds.contribution.submit));

    expect(screen.getByTestId(testIds.contribution.result)).toBeTruthy();
    expect(screen.getByText("R$ 72.500")).toBeTruthy();
    expect(screen.getByText("R$ 82.500")).toBeTruthy();
    expect(screen.getByText("12,1%")).toBeTruthy();
    expect(screen.getByText("+12,1 p.p.")).toBeTruthy();
    expect(screen.getByText("RECEBE O APORTE")).toBeTruthy();
    expect(
      screen.getByText(
        "Esta conta mostra apenas distribuição por classe. Não estima retorno, risco, imposto ou melhor investimento.",
      ),
    ).toBeTruthy();

    await user.clear(amountInput);

    expect(screen.queryByTestId(testIds.contribution.result)).toBeNull();
  });

  test("respeita o modo discreto no resultado", async () => {
    const user = userEvent.setup();
    await render(
      <ContributionSimulatorPanel hideAmounts snapshot={demoSnapshot} />,
    );

    await user.type(
      screen.getByTestId(testIds.contribution.amountInput),
      "5000",
    );
    await user.press(
      screen.getByTestId(testIds.contribution.classes.brazilEquity),
    );
    await user.press(screen.getByTestId(testIds.contribution.submit));

    expect(screen.getAllByText("R$ ••••••").length).toBeGreaterThanOrEqual(2);
  });
});
