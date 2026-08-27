import { ReactNode } from "react";
import {
  StyleProp,
  StyleSheet,
  Text,
  TextStyle,
  View,
  ViewStyle,
} from "react-native";

import { SignalTone } from "../domain/types";
import { colors, radius, shadow, spacing } from "../theme";

export function formatCurrency(value: number, hidden = false): string {
  if (hidden) {
    return "R$ ••••••";
  }
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

export function Surface({
  children,
  style,
}: {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
}) {
  return <View style={[styles.surface, style]}>{children}</View>;
}

export function Eyebrow({
  children,
  inverse = false,
  style,
}: {
  children: ReactNode;
  inverse?: boolean;
  style?: StyleProp<TextStyle>;
}) {
  return (
    <Text style={[styles.eyebrow, inverse && styles.eyebrowInverse, style]}>
      {children}
    </Text>
  );
}

export function SectionHeading({
  title,
  support,
}: {
  title: string;
  support?: string;
}) {
  return (
    <View style={styles.headingBlock}>
      <Text accessibilityRole="header" style={styles.heading}>
        {title}
      </Text>
      {support ? <Text style={styles.headingSupport}>{support}</Text> : null}
    </View>
  );
}

export function ToneBadge({
  tone,
  label,
}: {
  tone: SignalTone;
  label: string;
}) {
  return (
    <View
      style={[
        styles.badge,
        tone === "positive" && styles.badgePositive,
        tone === "attention" && styles.badgeAttention,
        tone === "neutral" && styles.badgeNeutral,
      ]}
    >
      <View
        accessibilityElementsHidden
        importantForAccessibility="no"
        style={[
          styles.badgeDot,
          tone === "positive" && styles.badgeDotPositive,
          tone === "attention" && styles.badgeDotAttention,
          tone === "neutral" && styles.badgeDotNeutral,
        ]}
      />
      <Text style={styles.badgeText}>{label}</Text>
    </View>
  );
}

export function DemoPill() {
  return (
    <View style={styles.demoPill}>
      <View style={styles.demoDot} />
      <Text style={styles.demoText}>DEMO SEGURA</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  surface: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    padding: spacing.md,
    ...shadow,
  },
  eyebrow: {
    color: colors.gold,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1.6,
    textTransform: "uppercase",
  },
  eyebrowInverse: {
    color: "#C9E8E2",
  },
  headingBlock: {
    gap: spacing.xxs,
  },
  heading: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "800",
    letterSpacing: -0.4,
  },
  headingSupport: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 21,
  },
  badge: {
    alignItems: "center",
    alignSelf: "flex-start",
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  badgePositive: {
    backgroundColor: colors.positiveSoft,
  },
  badgeAttention: {
    backgroundColor: colors.attentionSoft,
  },
  badgeNeutral: {
    backgroundColor: colors.neutralSoft,
  },
  badgeDot: {
    borderRadius: radius.pill,
    height: 7,
    width: 7,
  },
  badgeDotPositive: {
    backgroundColor: colors.positive,
  },
  badgeDotAttention: {
    backgroundColor: colors.attention,
  },
  badgeDotNeutral: {
    backgroundColor: colors.neutral,
  },
  badgeText: {
    color: colors.text,
    fontSize: 11,
    fontWeight: "700",
  },
  demoPill: {
    alignItems: "center",
    backgroundColor: colors.goldSoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  demoDot: {
    backgroundColor: colors.gold,
    borderRadius: radius.pill,
    height: 6,
    width: 6,
  },
  demoText: {
    color: "#714305",
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
});
