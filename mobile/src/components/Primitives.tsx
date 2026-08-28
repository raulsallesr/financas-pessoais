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

export function formatSnapshotDate(value: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value;
  }
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T12:00:00Z`)).replace(" de ", " ").replace(" de ", " ");
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
  return <DataModePill mode="demo" />;
}

export type PortfolioPresentationMode =
  | "loading"
  | "demo"
  | "local"
  | "unavailable"
  | "error";

export function PortfolioModePill({
  mode,
}: {
  mode: PortfolioPresentationMode;
}) {
  if (mode === "local") {
    return (
      <View
        accessibilityLabel="Carteira somente neste aparelho"
        style={[styles.contextPill, styles.contextPillLocal]}
      >
        <View style={[styles.contextDot, styles.contextDotLocal]} />
        <Text style={[styles.contextText, styles.contextTextLocal]}>
          SÓ NO APARELHO
        </Text>
      </View>
    );
  }
  if (mode === "error") {
    return (
      <View
        accessibilityLabel="Cofre local bloqueado"
        style={[styles.contextPill, styles.contextPillError]}
      >
        <View style={[styles.contextDot, styles.contextDotError]} />
        <Text style={[styles.contextText, styles.contextTextError]}>
          COFRE BLOQUEADO
        </Text>
      </View>
    );
  }
  if (mode === "loading") {
    return (
      <View accessibilityLabel="Verificando carteira" style={styles.contextPill}>
        <View style={styles.contextDot} />
        <Text style={styles.contextText}>VERIFICANDO</Text>
      </View>
    );
  }
  return <DemoPill />;
}

export function DataModePill({ mode }: { mode: "demo" | "live" }) {
  const live = mode === "live";
  return (
    <View
      accessibilityLabel={live ? "Dados públicos" : "Demonstração segura"}
      style={[styles.demoPill, live && styles.livePill]}
    >
      <View style={[styles.demoDot, live && styles.liveDot]} />
      <Text style={[styles.demoText, live && styles.liveText]}>
        {live ? "DADOS PÚBLICOS" : "DEMONSTRAÇÃO"}
      </Text>
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
  livePill: {
    backgroundColor: colors.primarySoft,
  },
  liveDot: {
    backgroundColor: colors.primary,
  },
  liveText: {
    color: colors.primaryDark,
  },
  demoText: {
    color: "#714305",
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
  contextPill: {
    alignItems: "center",
    backgroundColor: colors.neutralSoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  contextPillLocal: {
    backgroundColor: colors.primarySoft,
  },
  contextPillError: {
    backgroundColor: colors.dangerSoft,
  },
  contextDot: {
    backgroundColor: colors.neutral,
    borderRadius: radius.pill,
    height: 6,
    width: 6,
  },
  contextDotLocal: {
    backgroundColor: colors.primary,
  },
  contextDotError: {
    backgroundColor: colors.danger,
  },
  contextText: {
    color: colors.neutral,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
  contextTextLocal: {
    color: colors.primaryDark,
  },
  contextTextError: {
    color: colors.danger,
  },
});
