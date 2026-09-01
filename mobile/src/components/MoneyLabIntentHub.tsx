import { Pressable, StyleSheet, Text, useWindowDimensions, View } from "react-native";

import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, Surface } from "./Primitives";
import { MoneyLabSection, MoneyLabSession } from "./MoneyLabPanel";

const intentions: readonly {
  key: MoneyLabSection;
  index: string;
  title: string;
  support: string;
  testID: string;
}[] = [
  {
    key: "basics",
    index: "01",
    title: "Quero começar do zero",
    support: "Projeção, meta, espera, hábito e intuição.",
    testID: testIds.moneyLab.sections.basics,
  },
  {
    key: "explore",
    index: "02",
    title: "Quero enxergar o caminho",
    support: "Tempo, entradas, reserva e comparação completa.",
    testID: testIds.moneyLab.sections.explore,
  },
  {
    key: "life",
    index: "03",
    title: "Quero testar a vida real",
    support: "Aportes que mudam, compras parceladas e retiradas.",
    testID: testIds.moneyLab.sections.life,
  },
];

export function MoneyLabIntentHub({
  onSessionChange,
  session,
}: {
  onSessionChange: (session: MoneyLabSession) => void;
  session: MoneyLabSession;
}) {
  const { width } = useWindowDimensions();
  const compact = width < 420;

  return (
    <Surface style={styles.panel} testID={testIds.moneyLab.intentHub}>
      <View style={styles.heading}>
        <Eyebrow>Comece pela sua pergunta</Eyebrow>
        <Text accessibilityRole="header" style={styles.title}>
          O que você quer descobrir hoje?
        </Text>
        <Text style={styles.support}>
          Escolha uma intenção. O app mostra uma família por vez e guarda a
          brincadeira somente nesta sessão.
        </Text>
      </View>
      <View accessibilityRole="radiogroup" style={styles.grid}>
        {intentions.map((intention) => {
          const selected = session.section === intention.key;
          return (
            <Pressable
              accessibilityLabel={`${intention.title}. ${intention.support}`}
              accessibilityRole="radio"
              accessibilityState={{ selected }}
              key={intention.key}
              onPress={() =>
                onSessionChange({ ...session, section: intention.key })
              }
              style={({ pressed }) => [
                styles.option,
                compact && styles.optionCompact,
                selected && styles.optionSelected,
                pressed && styles.pressed,
              ]}
              testID={intention.testID}
            >
              <Text style={[styles.index, selected && styles.indexSelected]}>
                {intention.index}
              </Text>
              <Text style={[styles.optionTitle, selected && styles.titleSelected]}>
                {intention.title}
              </Text>
              <Text style={styles.optionSupport}>{intention.support}</Text>
            </Pressable>
          );
        })}
      </View>
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: { gap: spacing.md },
  heading: { gap: spacing.xs },
  title: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 30,
  },
  support: { color: colors.textMuted, fontSize: 14, lineHeight: 21 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  option: {
    backgroundColor: colors.surfaceMuted,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    boxSizing: "border-box",
    flexBasis: 180,
    flexGrow: 1,
    gap: 4,
    minHeight: 112,
    minWidth: 170,
    padding: spacing.sm,
  },
  optionCompact: { flexBasis: 142, minWidth: 136 },
  optionSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  index: {
    color: colors.textMuted,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1,
  },
  indexSelected: { color: colors.primary },
  optionTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
    lineHeight: 20,
  },
  titleSelected: { color: colors.primaryDark },
  optionSupport: { color: colors.textMuted, fontSize: 11, lineHeight: 16 },
  pressed: { opacity: 0.65 },
});
