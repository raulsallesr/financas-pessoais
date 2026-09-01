import { useState } from "react";
import {
  fireEvent,
  render,
  screen,
  userEvent,
  waitFor,
} from "@testing-library/react-native";

import { MoneyLifePanel } from "../../src/components/MoneyLifePanel";
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
    <MoneyLifePanel
      hideAmounts={hideAmounts}
      onSessionChange={setSession}
      session={session}
    />
  );
}

describe("MoneyLifePanel", () => {
  test("compara aporte fixo com aumento anual e pausa", async () => {
    await render(<Harness />);

    expect(screen.getByTestId(testIds.moneyLab.life.panel)).toBeTruthy();
    expect(
      screen.getByTestId(testIds.moneyLab.life.tools.flexible).props
        .accessibilityState,
    ).toEqual({ selected: true });
    expect(screen.getByText("COM O PLANO FLEXÍVEL")).toBeTruthy();
    expect(screen.getByText("Com aporte fixo")).toBeTruthy();
    expect(screen.getByText("Aportes pulados")).toBeTruthy();
    expect(screen.getByText("Aporte mensal no último ano")).toBeTruthy();
  });

  test("muda a pausa sem prometer reposição dos aportes", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByLabelText("12 meses"));

    expect(
      screen.getByText(/12 meses sem aporte no meio do prazo/),
    ).toBeTruthy();
    expect(
      screen.getByText(
        "A pausa começa aproximadamente na metade do prazo. O aumento anual continua no calendário mesmo durante a pausa.",
      ),
    ).toBeTruthy();
  });

  test("valida aumento anual somente depois do campo ser concluído", async () => {
    const invalidSession = {
      ...createMoneyLabSession(),
      annualContributionIncreaseText: "250",
    };
    await render(<Harness initialSession={invalidSession} />);

    expect(screen.queryByTestId(testIds.moneyLab.life.result)).toBeNull();
    expect(
      screen.queryByText("Use um aumento entre 0% e 200% ao ano."),
    ).toBeNull();

    await fireEvent(
      screen.getByTestId(testIds.moneyLab.life.increaseInput),
      "blur",
    );
    await waitFor(() =>
      expect(
        screen.getByText("Use um aumento entre 0% e 200% ao ano."),
      ).toBeTruthy(),
    );
  });

  test("soma parcelas e revela o custo implícito sem recomendar", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(
      screen.getByTestId(testIds.moneyLab.life.tools.installments),
    );

    expect(screen.getByText("TOTAL DAS PARCELAS")).toBeTruthy();
    expect(screen.getByText(/2\.880/)).toBeTruthy();
    expect(screen.getByText("Taxa implícita ao mês")).toBeTruthy();
    expect(
      screen.getByText(
        "A taxa implícita é a que iguala hoje o preço à vista às parcelas mensais informadas. Ela não é uma taxa anunciada pela loja.",
      ),
    ).toBeTruthy();
  });

  test("não inventa taxa positiva quando parcelar custa menos", async () => {
    const user = userEvent.setup();
    await render(
      <Harness
        initialSession={{
          ...createMoneyLabSession(),
          cashPriceText: "3000",
          lifeTool: "installments",
        }}
      />,
    );

    expect(screen.getByText("Sem taxa positiva")).toBeTruthy();
    expect(screen.getByText("Não se aplica")).toBeTruthy();
    await user.press(screen.getByLabelText("24 parcelas"));
    expect(screen.queryByText("Sem taxa positiva")).toBeNull();
  });

  test("modo discreto mascara valores em todas as experiências", async () => {
    const user = userEvent.setup();
    await render(<Harness hideAmounts />);

    expect(
      screen.getByTestId(testIds.moneyLab.life.initialInput).props
        .secureTextEntry,
    ).toBe(true);
    expect(screen.getAllByText("R$ ••••••").length).toBeGreaterThanOrEqual(2);

    await user.press(
      screen.getByTestId(testIds.moneyLab.life.tools.installments),
    );
    expect(
      screen.getByTestId(testIds.moneyLab.life.cashInput).props.secureTextEntry,
    ).toBe(true);
    expect(
      screen.getByTestId(testIds.moneyLab.life.installmentInput).props
        .secureTextEntry,
    ).toBe(true);

    await user.press(screen.getByTestId(testIds.moneyLab.life.tools.longevity));
    expect(
      screen.getByTestId(testIds.moneyLab.life.withdrawalInitialInput).props
        .secureTextEntry,
    ).toBe(true);
    expect(
      screen.getByTestId(testIds.moneyLab.life.withdrawalMonthlyInput).props
        .secureTextEntry,
    ).toBe(true);
  });

  test("mostra por quanto tempo o saldo atravessa as retiradas", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.life.tools.longevity));

    expect(screen.getByText("FÔLEGO DO CENÁRIO")).toBeTruthy();
    expect(screen.getByText("Como o saldo atravessa o tempo")).toBeTruthy();
    expect(screen.getByText("Total retirado")).toBeTruthy();
    expect(screen.getByText("Crescimento creditado")).toBeTruthy();
    expect(
      screen.getByText(
        "A retirada fica nominalmente igual durante todo o horizonte.",
      ),
    ).toBeTruthy();
  });

  test("revela o reajuste anual somente quando solicitado", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.life.tools.longevity));
    const toggle = screen.getByTestId(
      testIds.moneyLab.life.withdrawalInflationToggle,
    );
    expect(toggle.props.accessibilityState).toEqual({ checked: false });
    expect(
      screen.queryByTestId(testIds.moneyLab.life.withdrawalInflationInput),
    ).toBeNull();

    await user.press(toggle);

    expect(
      screen.getByTestId(testIds.moneyLab.life.withdrawalInflationToggle).props
        .accessibilityState,
    ).toEqual({ checked: true });
    expect(
      screen.getByTestId(testIds.moneyLab.life.withdrawalInflationInput),
    ).toBeTruthy();
    expect(screen.getByText(/A retirada aumenta 4,5%/)).toBeTruthy();
  });

  test("valida retirada inválida somente depois de concluir o campo", async () => {
    const invalidSession = {
      ...createMoneyLabSession(),
      lifeTool: "longevity" as const,
      withdrawalMonthlyText: "0",
    };
    await render(<Harness initialSession={invalidSession} />);

    expect(screen.queryByTestId(testIds.moneyLab.life.result)).toBeNull();
    expect(
      screen.queryByText("Informe uma retirada mensal positiva."),
    ).toBeNull();

    await fireEvent(
      screen.getByTestId(testIds.moneyLab.life.withdrawalMonthlyInput),
      "blur",
    );
    await waitFor(() =>
      expect(
        screen.getByText("Informe uma retirada mensal positiva."),
      ).toBeTruthy(),
    );
  });
});
