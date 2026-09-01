import { useState } from "react";
import { render, screen, userEvent } from "@testing-library/react-native";

import { MoneyLabIntentHub } from "../../src/components/MoneyLabIntentHub";
import {
  createMoneyLabSession,
  MoneyLabSession,
} from "../../src/components/MoneyLabPanel";
import testIds from "../../src/testing/testIds.json";

function Harness() {
  const [session, setSession] = useState<MoneyLabSession>(createMoneyLabSession);
  return <MoneyLabIntentHub onSessionChange={setSession} session={session} />;
}

describe("MoneyLabIntentHub", () => {
  test("começa por uma intenção reconhecível sem criar nova aba", async () => {
    await render(<Harness />);

    expect(screen.getByTestId(testIds.moneyLab.intentHub)).toBeTruthy();
    expect(screen.getAllByRole("radio")).toHaveLength(3);
    expect(
      screen.getByTestId(testIds.moneyLab.sections.basics).props
        .accessibilityState,
    ).toEqual({ selected: true });
    expect(screen.getByText("O que você quer descobrir hoje?")).toBeTruthy();
  });

  test("troca de família e preserva uma escolha explícita", async () => {
    const user = userEvent.setup();
    await render(<Harness />);

    await user.press(screen.getByTestId(testIds.moneyLab.sections.life));

    expect(
      screen.getByTestId(testIds.moneyLab.sections.life).props.accessibilityState,
    ).toEqual({ selected: true });
    expect(
      screen.getByTestId(testIds.moneyLab.sections.basics).props
        .accessibilityState,
    ).toEqual({ selected: false });
  });
});
