import { useState } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  DemoPill,
  Eyebrow,
  formatCurrency,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import {
  allocationPercent,
  portfolioTotal,
} from "../domain/insights";
import { MarketSnapshot } from "../domain/types";
import { colors, radius, spacing } from "../theme";

export function PortfolioScreen({ snapshot }: { snapshot: MarketSnapshot }) {
  const [hidden, setHidden] = useState(false);
  const total = portfolioTotal(snapshot);
  const sorted = [...snapshot.positions].sort((a, b) => b.amount - a.amount);

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerRow}>
        <View style={styles.headerCopy}>
          <Eyebrow>Sua fotografia</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            Carteira
          </Text>
        </View>
        <DemoPill />
      </View>

      <View style={styles.balanceCard}>
        <View style={styles.balanceTopline}>
          <Text style={styles.balanceLabel}>Patrimônio acompanhado</Text>
          <Pressable
            accessibilityLabel={hidden ? "Mostrar valores" : "Ocultar valores"}
            accessibilityRole="button"
            onPress={() => setHidden((value) => !value)}
            style={({ pressed }) => [
              styles.privacyButton,
              pressed && styles.pressed,
            ]}
          >
            <View style={[styles.privacyDot, hidden && styles.privacyDotHidden]} />
            <Text style={styles.privacyText}>{hidden ? "Mostrar" : "Ocultar"}</Text>
          </Pressable>
        </View>
        <Text style={styles.balanceValue}>{formatCurrency(total, hidden)}</Text>
        <Text style={styles.balanceSupport}>
          {snapshot.positions.length} posições · dados sintéticos neste corte
        </Text>
      </View>

      <SectionHeading
        title="Onde você está exposto"
        support="A barra mostra peso, não qualidade nem recomendação."
      />
      <Surface style={styles.allocationCard}>
        {sorted.map((position) => {
          const allocation = allocationPercent(snapshot, position.amount);
          return (
            <View key={position.id} style={styles.allocationRow}>
              <View style={styles.allocationTopline}>
                <View style={styles.positionCopy}>
                  <Text style={styles.positionName}>{position.shortName}</Text>
                  <Text style={styles.positionClass}>{position.assetClass}</Text>
                </View>
                <View style={styles.positionValue}>
                  <Text style={styles.positionAmount}>
                    {formatCurrency(position.amount, hidden)}
                  </Text>
                  <Text style={styles.positionPercent}>
                    {allocation.toFixed(1).replace(".", ",")}%
                  </Text>
                </View>
              </View>
              <View
                accessible
                accessibilityLabel={`${position.shortName}: ${allocation.toFixed(
                  1,
                )}% da carteira`}
                style={styles.track}
              >
                <View style={[styles.bar, { width: `${allocation}%` }]} />
              </View>
            </View>
          );
        })}
      </Surface>

      <SectionHeading title="Privacidade desde o começo" />
      <View style={styles.privacyCard}>
        <View style={styles.lockMark}>
          <View style={styles.lockArc} />
          <View style={styles.lockBody} />
        </View>
        <View style={styles.privacyCopy}>
          <Text style={styles.privacyTitle}>Carteira local por padrão</Text>
          <Text style={styles.privacySupport}>
            O produto final armazenará posições no aparelho e pedirá consentimento
            explícito antes de qualquer sincronização. Esta versão usa somente uma
            carteira fictícia.
          </Text>
        </View>
      </View>

      <Surface style={styles.nextCard}>
        <Eyebrow>Próximo incremento</Eyebrow>
        <Text style={styles.nextTitle}>Montar ou importar sua carteira</Text>
        <Text style={styles.nextSupport}>
          Editor móvel, importação B3 sanitizada e armazenamento criptografado
          entram depois do contrato de dados do app ser fechado.
        </Text>
      </Surface>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    alignSelf: "center",
    gap: spacing.lg,
    maxWidth: 820,
    paddingBottom: spacing.xl,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.md,
    width: "100%",
  },
  headerRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  headerCopy: {
    gap: spacing.xxs,
  },
  title: {
    color: colors.text,
    fontSize: 31,
    fontWeight: "900",
    letterSpacing: -1,
  },
  balanceCard: {
    backgroundColor: colors.primaryDark,
    borderRadius: radius.lg,
    gap: spacing.xs,
    padding: spacing.lg,
  },
  balanceTopline: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  balanceLabel: {
    color: "#C9E8E2",
    fontSize: 12,
    fontWeight: "700",
  },
  balanceValue: {
    color: colors.white,
    fontSize: 34,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    letterSpacing: -1,
  },
  balanceSupport: {
    color: "#A9D2CA",
    fontSize: 12,
  },
  privacyButton: {
    alignItems: "center",
    backgroundColor: "rgba(255,255,255,0.12)",
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    minHeight: 48,
    paddingHorizontal: 12,
  },
  privacyDot: {
    backgroundColor: "#8FD3C5",
    borderRadius: radius.pill,
    height: 8,
    width: 8,
  },
  privacyDotHidden: {
    backgroundColor: "#F8CF8B",
  },
  privacyText: {
    color: colors.white,
    fontSize: 11,
    fontWeight: "700",
  },
  allocationCard: {
    gap: spacing.lg,
  },
  allocationRow: {
    gap: spacing.xs,
  },
  allocationTopline: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  positionCopy: {
    flex: 1,
    gap: 2,
  },
  positionName: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "800",
  },
  positionClass: {
    color: colors.textMuted,
    fontSize: 11,
  },
  positionValue: {
    alignItems: "flex-end",
  },
  positionAmount: {
    color: colors.text,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  positionPercent: {
    color: colors.primary,
    fontSize: 11,
    fontWeight: "800",
  },
  track: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.pill,
    height: 8,
    overflow: "hidden",
  },
  bar: {
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: "100%",
  },
  privacyCard: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    flexDirection: "row",
    gap: spacing.md,
    padding: spacing.md,
  },
  lockMark: {
    alignItems: "center",
    height: 46,
    justifyContent: "flex-end",
    width: 40,
  },
  lockArc: {
    borderColor: colors.primary,
    borderRadius: 12,
    borderWidth: 3,
    height: 22,
    position: "absolute",
    top: 1,
    width: 24,
  },
  lockBody: {
    backgroundColor: colors.primary,
    borderRadius: 7,
    height: 29,
    width: 34,
  },
  privacyCopy: {
    flex: 1,
    gap: spacing.xxs,
  },
  privacyTitle: {
    color: colors.primaryDark,
    fontSize: 16,
    fontWeight: "900",
  },
  privacySupport: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  nextCard: {
    gap: spacing.xs,
  },
  nextTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "900",
  },
  nextSupport: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  pressed: {
    opacity: 0.65,
  },
});
