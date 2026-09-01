import { useState } from "react";
import { render, screen, userEvent } from "@testing-library/react-native";

import { MoneyLabExpansionPanel } from "../../src/components/MoneyLabExpansionPanel";
import {
  createMoneyLabSession,
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
    <MoneyLabExpansionPanel
      hideAmounts={hideAmounts}
      onSessionChange={setSession}
      session={session}
    />
  );
}

describe("MoneyLabExpansionPanel", () => {
  test("começa pelo poder do tempo com dobra, régua e marcos", async () => {
    await render(<Harness />);

    expect(screen.getByTestId(testIds.moneyLab.expansion.panel)).toBeTruthy();
    expect(
      screen.getByTestId(testIds.moneyLab.expansion.tools.time).props
        .accessibilityState,
    ).toEqual({ selected: true });
    expect(screen.getByText("Quando o valor inicial dobra?")).toBeTruthy();
    expect(screen.getByText("Marcos da jornada")).toBeTruthy();
    expect(screen.getByLabelText(/10\.000/)).toBeTruthy();
    expect(screen.getByTestId(testIds.moneyLab.expansion.result)).toBeTruthy();
  });

  test("régua altera o prazo por passo e por marco tocável", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.expansion.yearPlus));
    expect(screen.getByText("11 anos")).toBeTruthy();

    await user.press(screen.getByLabelText("20 anos"));
    expect(screen.getByText("20 anos")).toBeTruthy();
    expect(screen.getByText("NO PONTO ESCOLHIDO DA RÉGUA")).toBeTruthy();
  });

  test("traduz o mês e compara aporte extra anual", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.tools.income),
    );
    expect(
      screen.getByText("Quanto rende no mês e o que um extra muda?"),
    ).toBeTruthy();
    expect(screen.getByText("EQUIVALENTE DE UM MÊS")).toBeTruthy();

    await user.press(screen.getByText("Todo fim de ano"));
    expect(screen.getByText("Extra colocado")).toBeTruthy();
    expect(
      screen.getByText(
        "Equivalente mensal não significa pagamento mensal, renda garantida ou liquidez. O extra não representa produto, 13º real ou obrigação.",
      ),
    ).toBeTruthy();
  });

  test("mostra caminho da reserva e ausência de prazo com aporte zero", async () => {
    const user = userEvent.setup();
    await render(
      <Harness
        initialSession={{
          ...createMoneyLabSession(),
          reserveContributionText: "0",
        }}
      />,
    );

    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.tools.reserve),
    );
    expect(screen.getByText("Quantos meses minha reserva cobre?")).toBeTruthy();
    expect(screen.getByText("2,0 meses")).toBeTruthy();
    expect(screen.getByText("Sem prazo com aporte zero")).toBeTruthy();
  });

  test("revela inflação e custo somente quando solicitados", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.tools.complete),
    );
    expect(screen.queryByTestId(testIds.moneyLab.expansion.costInput)).toBeNull();
    expect(
      screen.queryByTestId(testIds.moneyLab.expansion.inflationInput),
    ).toBeNull();

    await user.press(screen.getByTestId(testIds.moneyLab.expansion.costToggle));
    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.inflationToggle),
    );

    expect(screen.getByTestId(testIds.moneyLab.expansion.costInput)).toBeTruthy();
    expect(
      screen.getByTestId(testIds.moneyLab.expansion.inflationInput),
    ).toBeTruthy();
    expect(screen.getByText("Efeito acumulado do custo")).toBeTruthy();
    expect(screen.getByText("Com aportes, em dinheiro de hoje")).toBeTruthy();
  });

  test("modo discreto mascara também reserva e bônus", async () => {
    const user = userEvent.setup();
    await render(<Harness hideAmounts />);

    expect(
      screen.getByText(
        "Modo discreto ativo: entradas e resultados monetários estão ocultos.",
      ),
    ).toBeTruthy();

    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.tools.income),
    );
    expect(
      screen.getByTestId(testIds.moneyLab.expansion.bonusInput).props
        .secureTextEntry,
    ).toBe(true);

    await user.press(
      screen.getByTestId(testIds.moneyLab.expansion.tools.reserve),
    );
    expect(
      screen.getByTestId(testIds.moneyLab.expansion.reserveCurrentInput).props
        .secureTextEntry,
    ).toBe(true);
    expect(screen.getAllByText("R$ ••••••").length).toBeGreaterThanOrEqual(2);
  });
});
