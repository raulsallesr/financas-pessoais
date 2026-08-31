import { render, screen, userEvent } from "@testing-library/react-native";

import { BottomNav } from "../../src/components/BottomNav";
import testIds from "../../src/testing/testIds.json";

describe("BottomNav", () => {
  test("mantém quatro destinos semânticos e anuncia o selecionado", async () => {
    await render(<BottomNav activeTab="today" onChange={jest.fn()} />);

    expect(screen.getAllByRole("tab")).toHaveLength(4);
    expect(screen.getByTestId(testIds.tabs.today).props.accessibilityState).toEqual({
      selected: true,
    });
    expect(
      screen.getByTestId(testIds.tabs.scenarios).props.accessibilityState,
    ).toEqual({ selected: false });
  });

  test("entrega a navegação escolhida sem alterar estado internamente", async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    await render(<BottomNav activeTab="today" onChange={onChange} />);

    await user.press(screen.getByTestId(testIds.tabs.scenarios));

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith("scenarios");
    expect(screen.getByTestId(testIds.tabs.today).props.accessibilityState).toEqual({
      selected: true,
    });
  });
});
