import { Pressable, StyleSheet, Text, View } from "react-native";

import testIds from "../testing/testIds.json";
import { colors, spacing } from "../theme";

export type TabKey = "today" | "portfolio" | "scenarios" | "learn";

const tabs: readonly { key: TabKey; label: string }[] = [
  { key: "today", label: "Hoje" },
  { key: "portfolio", label: "Carteira" },
  { key: "scenarios", label: "Cenários" },
  { key: "learn", label: "Entenda" },
];

function TabGlyph({ type, active }: { type: TabKey; active: boolean }) {
  const color = active ? colors.primary : colors.textMuted;
  if (type === "today") {
    return (
      <View style={styles.gridIcon}>
        {[0, 1, 2, 3].map((item) => (
          <View key={item} style={[styles.gridDot, { backgroundColor: color }]} />
        ))}
      </View>
    );
  }
  if (type === "portfolio") {
    return (
      <View style={[styles.walletIcon, { borderColor: color }]}>
        <View style={[styles.walletLine, { backgroundColor: color }]} />
      </View>
    );
  }
  if (type === "scenarios") {
    return (
      <View style={styles.chartIcon}>
        <View style={[styles.chartAxis, { backgroundColor: color }]} />
        <View style={[styles.chartBarSmall, { backgroundColor: color }]} />
        <View style={[styles.chartBarLarge, { backgroundColor: color }]} />
      </View>
    );
  }
  return (
    <View style={[styles.infoIcon, { borderColor: color }]}>
      <View style={[styles.infoDot, { backgroundColor: color }]} />
      <View style={[styles.infoLine, { backgroundColor: color }]} />
    </View>
  );
}

export function BottomNav({
  activeTab,
  onChange,
}: {
  activeTab: TabKey;
  onChange: (tab: TabKey) => void;
}) {
  return (
    <View accessibilityRole="tablist" style={styles.bar}>
      {tabs.map((tab) => {
        const active = tab.key === activeTab;
        return (
          <Pressable
            accessibilityLabel={`Abrir ${tab.label}`}
            accessibilityRole="tab"
            accessibilityState={{ selected: active }}
            aria-selected={active}
            key={tab.key}
            onPress={() => onChange(tab.key)}
            style={({ pressed }) => [styles.tab, pressed && styles.tabPressed]}
            testID={testIds.tabs[tab.key]}
          >
            <TabGlyph active={active} type={tab.key} />
            <Text style={[styles.label, active && styles.labelActive]}>
              {tab.label}
            </Text>
            <View style={[styles.indicator, active && styles.indicatorActive]} />
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    backgroundColor: colors.surface,
    borderTopColor: colors.border,
    borderTopWidth: 1,
    flexDirection: "row",
    minHeight: 72,
    paddingHorizontal: spacing.xs,
  },
  tab: {
    alignItems: "center",
    flex: 1,
    gap: 4,
    justifyContent: "center",
    minHeight: 56,
    minWidth: 64,
    paddingTop: spacing.xs,
  },
  tabPressed: {
    opacity: 0.6,
  },
  label: {
    color: colors.textMuted,
    fontSize: 11,
    fontWeight: "700",
  },
  labelActive: {
    color: colors.primary,
  },
  indicator: {
    backgroundColor: "transparent",
    borderRadius: 2,
    height: 3,
    width: 20,
  },
  indicatorActive: {
    backgroundColor: colors.primary,
  },
  gridIcon: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 3,
    height: 17,
    width: 17,
  },
  gridDot: {
    borderRadius: 2,
    height: 7,
    width: 7,
  },
  walletIcon: {
    borderRadius: 4,
    borderWidth: 2,
    height: 16,
    justifyContent: "center",
    paddingHorizontal: 3,
    width: 21,
  },
  walletLine: {
    borderRadius: 2,
    height: 2,
    width: 7,
  },
  chartIcon: {
    alignItems: "flex-end",
    flexDirection: "row",
    gap: 3,
    height: 18,
    paddingBottom: 2,
    width: 21,
  },
  chartAxis: {
    bottom: 0,
    height: 2,
    left: 0,
    position: "absolute",
    width: 21,
  },
  chartBarSmall: {
    borderRadius: 2,
    height: 8,
    marginLeft: 3,
    width: 5,
  },
  chartBarLarge: {
    borderRadius: 2,
    height: 14,
    width: 5,
  },
  infoIcon: {
    alignItems: "center",
    borderRadius: 10,
    borderWidth: 2,
    height: 19,
    justifyContent: "center",
    width: 19,
  },
  infoDot: {
    borderRadius: 2,
    height: 3,
    marginBottom: 2,
    width: 3,
  },
  infoLine: {
    borderRadius: 2,
    height: 7,
    width: 2,
  },
});
