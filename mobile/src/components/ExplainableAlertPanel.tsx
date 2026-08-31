import {
  Pressable,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";

import { ExplainableAlert } from "../domain/explainableAlerts";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, Surface, ToneBadge } from "./Primitives";

export function ExplainableAlertPanel({
  alert,
  favorite,
  favoriteMessage,
  favoriteSaving,
  onToggleFavorite,
}: {
  alert: ExplainableAlert;
  favorite: boolean;
  favoriteMessage?: string;
  favoriteSaving: boolean;
  onToggleFavorite: () => void;
}) {
  const { width } = useWindowDimensions();
  const isWide = width >= 720;
  const evidence = [
    { label: "O que mudou", value: alert.whatChanged },
    { label: "O que prova", value: alert.whatProves },
    { label: "Onde afeta", value: alert.whereItAffects },
    { label: "O que não prova", value: alert.whatItDoesNotProve },
  ];

  return (
    <Surface style={styles.panel}>
      <View style={styles.header}>
        <View style={styles.headerCopy}>
          <Eyebrow>Alerta explicável</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            {alert.signal.label}
          </Text>
          <ToneBadge
            label={alert.signal.tone === "attention" ? "pede atenção" : "acompanhar"}
            tone={alert.signal.tone}
          />
        </View>
        <Pressable
          accessibilityHint="Mantém este sinal no início da lista neste aparelho"
          accessibilityLabel={favorite ? "Remover dos favoritos" : "Adicionar aos favoritos"}
          accessibilityRole="switch"
          accessibilityState={{ checked: favorite, disabled: favoriteSaving }}
          disabled={favoriteSaving}
          onPress={onToggleFavorite}
          style={({ pressed }) => [
            styles.favoriteButton,
            favorite && styles.favoriteButtonActive,
            (pressed || favoriteSaving) && styles.pressed,
          ]}
        >
          <View
            accessibilityElementsHidden
            importantForAccessibility="no"
            style={[styles.favoriteMark, favorite && styles.favoriteMarkActive]}
          />
          <Text
            style={[
              styles.favoriteButtonText,
              favorite && styles.favoriteButtonTextActive,
            ]}
          >
            {favoriteSaving
              ? "Salvando"
              : favorite
                ? "Acompanhando"
                : "Acompanhar"}
          </Text>
        </Pressable>
      </View>

      {favoriteMessage ? (
        <Text accessibilityLiveRegion="polite" style={styles.favoriteMessage}>
          {favoriteMessage}
        </Text>
      ) : null}

      <View style={[styles.evidenceGrid, isWide && styles.evidenceGridWide]}>
        {evidence.map((item) => (
          <View
            key={item.label}
            style={[styles.evidenceItem, isWide && styles.evidenceItemWide]}
          >
            <Text style={styles.evidenceLabel}>{item.label}</Text>
            <Text style={styles.evidenceValue}>{item.value}</Text>
          </View>
        ))}
      </View>
    </Surface>
  );
}

const styles = StyleSheet.create({
  panel: {
    gap: spacing.md,
  },
  header: {
    alignItems: "flex-start",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
    justifyContent: "space-between",
  },
  headerCopy: {
    flex: 1,
    gap: spacing.xs,
    minWidth: 190,
  },
  title: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
    lineHeight: 26,
  },
  favoriteButton: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.xs,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  favoriteButtonActive: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
  },
  favoriteMark: {
    borderColor: colors.primary,
    borderRadius: 3,
    borderWidth: 2,
    height: 14,
    width: 14,
  },
  favoriteMarkActive: {
    backgroundColor: colors.primary,
    borderWidth: 4,
  },
  favoriteButtonText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "900",
  },
  favoriteButtonTextActive: {
    color: colors.primaryDark,
  },
  favoriteMessage: {
    color: colors.textMuted,
    fontSize: 12,
    lineHeight: 18,
  },
  evidenceGrid: {
    gap: spacing.sm,
  },
  evidenceGridWide: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  evidenceItem: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    gap: spacing.xs,
    padding: spacing.md,
  },
  evidenceItemWide: {
    width: "49%",
  },
  evidenceLabel: {
    color: colors.primaryDark,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0.7,
    textTransform: "uppercase",
  },
  evidenceValue: {
    color: colors.text,
    fontSize: 13,
    lineHeight: 20,
  },
  pressed: {
    opacity: 0.65,
  },
});
