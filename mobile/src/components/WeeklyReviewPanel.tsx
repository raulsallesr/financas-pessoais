import {
  Pressable,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from "react-native";

import { buildExplainableAlert } from "../domain/explainableAlerts";
import { impactsForSignal, signalById } from "../domain/insights";
import {
  comparePublicSnapshots,
  PublicSnapshotHistoryV1,
} from "../domain/snapshotHistory";
import { MarketSignal, MarketSnapshot } from "../domain/types";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";
import { Eyebrow, formatSnapshotDate, Surface, ToneBadge } from "./Primitives";

export type WeeklyReviewStep = 0 | 1 | 2 | 3 | 4;

type ReviewTopic = {
  label: string;
  explanation: string;
};

function topicForSignal(signal: MarketSignal): ReviewTopic {
  if (signal.source.toLocaleLowerCase("pt-BR").includes("focus")) {
    return {
      label: "Boletim Focus",
      explanation:
        "Expectativa declarada por participantes, sempre lida com indicador, horizonte, data e dispersão.",
    };
  }
  if (
    signal.id === "curva" ||
    signal.source.toLocaleLowerCase("pt-BR").includes("tesouro")
  ) {
    return {
      label: "Curva de juros",
      explanation:
        "Taxas observadas também carregam prêmio de prazo, liquidez, risco e condições do título.",
    };
  }
  return {
    label: "Contexto de mercado",
    explanation:
      "Um sinal auxiliar ajuda a organizar a leitura, mas não substitui evidência nem cria causalidade.",
  };
}

function literalChangeCopy(
  history: PublicSnapshotHistoryV1 | null,
  signal: MarketSignal,
): { title: string; text: string } {
  const current = history?.snapshots[0] ?? null;
  const previous = history?.snapshots[1] ?? null;
  if (!current || !previous) {
    return {
      title: "Ainda sem duas fotografias comparáveis",
      text: `A leitura atual registra ${signal.value} (${signal.change}). Quando houver outra fotografia pública compatível, a comparação literal aparecerá aqui.`,
    };
  }

  const comparison = comparePublicSnapshots(current, previous);
  const change = comparison.signalChanges.find((item) => item.id === signal.id);
  const interval = `${formatSnapshotDate(previous.asOf)} → ${formatSnapshotDate(current.asOf)}`;
  if (!change) {
    return {
      title: "Sem mudança literal neste sinal",
      text: `Entre ${interval}, valor, movimento, destaque e tom permaneceram iguais no histórico local.`,
    };
  }
  if (change.kind === "added") {
    return {
      title: "O sinal entrou na fotografia",
      text: `Entre ${interval}, ele passou a aparecer com ${change.currentValue}.`,
    };
  }
  if (change.kind === "removed") {
    return {
      title: "O sinal saiu da fotografia",
      text: `Entre ${interval}, a leitura anterior de ${change.previousValue} deixou de aparecer.`,
    };
  }
  return {
    title: "O histórico registrou uma mudança literal",
    text: `Entre ${interval}, o valor foi de ${change.previousValue} para ${change.currentValue}. A comparação também preserva movimento, destaque e tom sem reinterpretá-los.`,
  };
}

export function WeeklyReviewPanel({
  favorite,
  history,
  onCancel,
  onExploreScenarios,
  onFinish,
  onStepChange,
  signalId,
  snapshot,
  step,
}: {
  favorite: boolean;
  history: PublicSnapshotHistoryV1 | null;
  onCancel: () => void;
  onExploreScenarios: () => void;
  onFinish: () => void;
  onStepChange: (step: WeeklyReviewStep) => void;
  signalId: string;
  snapshot: MarketSnapshot;
  step: WeeklyReviewStep;
}) {
  const { width } = useWindowDimensions();
  const isWide = width >= 720;
  const signal = signalById(snapshot, signalId);
  const alert = buildExplainableAlert(snapshot, signalId);
  const impacts = impactsForSignal(snapshot, signalId);
  const change = literalChangeCopy(history, signal);
  const topic = topicForSignal(signal);
  const stepNumber = step + 1;

  return (
    <Surface style={styles.panel} testID={testIds.weeklyReview.panel}>
      <View style={styles.header}>
        <View style={styles.headerCopy}>
          <Eyebrow>Revisão guiada · {stepNumber} de 5</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>
            {signal.label}
          </Text>
          <View style={styles.badgeRow}>
            <ToneBadge
              label={signal.tone === "attention" ? "pede atenção" : "acompanhar"}
              tone={signal.tone}
            />
            {favorite ? (
              <View style={styles.favoritePill}>
                <Text style={styles.favoriteText}>Acompanhando</Text>
              </View>
            ) : null}
          </View>
        </View>
        <Pressable
          accessibilityHint="Fecha a revisão sem alterar a carteira"
          accessibilityLabel="Encerrar revisão guiada"
          accessibilityRole="button"
          onPress={onCancel}
          style={({ pressed }) => [
            styles.closeButton,
            pressed && styles.pressed,
          ]}
          testID={testIds.weeklyReview.cancel}
        >
          <Text style={styles.closeButtonText}>Agora não</Text>
        </Pressable>
      </View>

      <View
        accessibilityLabel={`Passo ${stepNumber} de 5`}
        accessibilityRole="progressbar"
        accessibilityValue={{ max: 5, min: 1, now: stepNumber }}
        style={styles.progressTrack}
        testID={testIds.weeklyReview.progress}
      >
        {[0, 1, 2, 3, 4].map((item) => (
          <View
            key={item}
            style={[
              styles.progressSegment,
              item <= step && styles.progressSegmentActive,
            ]}
          />
        ))}
      </View>

      <View accessibilityLiveRegion="polite" style={styles.stepContent}>
        {step === 0 ? (
          <>
            <Text style={styles.stepLabel}>O QUE MUDOU</Text>
            <Text style={styles.stepTitle}>{change.title}</Text>
            <Text style={styles.stepText}>{change.text}</Text>
            <View style={styles.contextCard}>
              <Text style={styles.contextLabel}>LEITURA ATUAL</Text>
              <Text style={styles.contextTitle}>{signal.headline}</Text>
              <Text style={styles.contextText}>{signal.explanation}</Text>
            </View>
          </>
        ) : null}

        {step === 1 ? (
          <>
            <Text style={styles.stepLabel}>O QUE PROVA</Text>
            <Text style={styles.stepTitle}>Número, movimento, fonte e data</Text>
            <Text style={styles.stepText}>{alert.whatProves}</Text>
            <View style={styles.topicCard}>
              <Text style={styles.topicLabel}>TÓPICO RELACIONADO</Text>
              <Text style={styles.topicTitle}>{topic.label}</Text>
              <Text style={styles.topicText}>{topic.explanation}</Text>
            </View>
          </>
        ) : null}

        {step === 2 ? (
          <>
            <Text style={styles.stepLabel}>ONDE TOCA A CARTEIRA</Text>
            <Text style={styles.stepTitle}>
              {impacts.length
                ? `${impacts.length} ${impacts.length === 1 ? "posição relacionada" : "posições relacionadas"}`
                : "Sem efeito classificado para este recorte"}
            </Text>
            <Text style={styles.stepText}>{alert.whereItAffects}</Text>
            {impacts.length ? (
              <View style={[styles.impactGrid, isWide && styles.impactGridWide]}>
                {impacts.slice(0, 4).map((impact) => (
                  <View
                    key={impact.position.id}
                    style={[styles.impactRow, isWide && styles.impactRowWide]}
                  >
                    <View style={styles.impactCopy}>
                      <Text style={styles.impactName}>
                        {impact.position.shortName}
                      </Text>
                      <Text style={styles.impactEffect}>
                        {impact.effect.headline}
                      </Text>
                    </View>
                    <Text style={styles.impactPercent}>
                      {impact.allocationPercent.toFixed(0)}%
                    </Text>
                  </View>
                ))}
                {impacts.length > 4 ? (
                  <Text style={styles.moreText}>
                    +{impacts.length - 4} posições preservadas no recorte de Hoje
                  </Text>
                ) : null}
              </View>
            ) : (
              <View style={styles.limitState}>
                <Text style={styles.limitStateText}>
                  Sem relação declarada continua sem relação: a revisão não
                  aproxima classe, posição ou impacto.
                </Text>
              </View>
            )}
          </>
        ) : null}

        {step === 3 ? (
          <>
            <Text style={styles.stepLabel}>O QUE EXPLORAR EM CENÁRIOS</Text>
            <Text style={styles.stepTitle}>Escolha você mesmo uma hipótese</Text>
            <Text style={styles.stepText}>
              Abra Cenários para testar distribuição ou sensibilidade com as
              ferramentas já existentes. A revisão não preenche valor, classe ou
              choque e não altera a carteira.
            </Text>
            <View style={styles.contextCard}>
              <Text style={styles.contextLabel}>PONTO DE PARTIDA</Text>
              <Text style={styles.contextTitle}>
                {impacts.length
                  ? "Observe como as relações já classificadas respondem"
                  : "Explore a hipótese sem atribuí-la a este sinal"}
              </Text>
              <Text style={styles.contextText}>
                {impacts.length
                  ? "As posições e os efeitos continuam os mesmos que você acabou de revisar."
                  : "Sem efeito classificado, Cenários permanece uma ferramenta educacional separada."}
              </Text>
            </View>
          </>
        ) : null}

        {step === 4 ? (
          <>
            <Text style={styles.stepLabel}>O QUE NÃO PROVA</Text>
            <Text style={styles.stepTitle}>A leitura termina no próprio limite</Text>
            <Text style={styles.stepText}>{alert.whatItDoesNotProve}</Text>
            <View style={styles.limitState}>
              <Text style={styles.limitStateText}>
                A revisão organiza evidência pública e exposição local. Ela não
                cria urgência, retorno previsto, recomendação ou ordem.
              </Text>
            </View>
          </>
        ) : null}
      </View>

      <View style={styles.actions}>
        {step > 0 ? (
          <Pressable
            accessibilityLabel="Voltar ao passo anterior"
            accessibilityRole="button"
            onPress={() => onStepChange((step - 1) as WeeklyReviewStep)}
            style={({ pressed }) => [
              styles.secondaryButton,
              pressed && styles.pressed,
            ]}
            testID={testIds.weeklyReview.previous}
          >
            <Text style={styles.secondaryButtonText}>Voltar</Text>
          </Pressable>
        ) : null}

        {step < 3 ? (
          <Pressable
            accessibilityLabel="Continuar revisão guiada"
            accessibilityRole="button"
            onPress={() => onStepChange((step + 1) as WeeklyReviewStep)}
            style={({ pressed }) => [
              styles.primaryButton,
              pressed && styles.pressed,
            ]}
            testID={testIds.weeklyReview.next}
          >
            <Text style={styles.primaryButtonText}>Continuar</Text>
            <Text accessibilityElementsHidden style={styles.buttonArrow}>→</Text>
          </Pressable>
        ) : null}

        {step === 3 ? (
          <View style={styles.scenarioActions}>
            <Pressable
              accessibilityHint="Não altera valor, classe, choque ou carteira"
              accessibilityLabel="Abrir Cenários para escolher uma hipótese"
              accessibilityRole="button"
              onPress={onExploreScenarios}
              style={({ pressed }) => [
                styles.primaryButton,
                pressed && styles.pressed,
              ]}
              testID={testIds.weeklyReview.exploreScenarios}
            >
              <Text style={styles.primaryButtonText}>Explorar em Cenários</Text>
              <Text accessibilityElementsHidden style={styles.buttonArrow}>→</Text>
            </Pressable>
            <Pressable
              accessibilityLabel="Continuar para o limite sem abrir Cenários"
              accessibilityRole="button"
              onPress={() => onStepChange(4)}
              style={({ pressed }) => [
                styles.textButton,
                pressed && styles.pressed,
              ]}
            >
              <Text style={styles.textButtonText}>Continuar sem abrir</Text>
            </Pressable>
          </View>
        ) : null}

        {step === 4 ? (
          <Pressable
            accessibilityHint="Fecha a revisão e volta ao sinal selecionado em Hoje"
            accessibilityLabel="Concluir revisão e voltar para Hoje"
            accessibilityRole="button"
            onPress={onFinish}
            style={({ pressed }) => [
              styles.primaryButton,
              pressed && styles.pressed,
            ]}
            testID={testIds.weeklyReview.finish}
          >
            <Text style={styles.primaryButtonText}>Voltar ao sinal em Hoje</Text>
            <Text accessibilityElementsHidden style={styles.buttonArrow}>→</Text>
          </Pressable>
        ) : null}
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
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: -0.4,
    lineHeight: 28,
  },
  badgeRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
  },
  favoritePill: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  favoriteText: {
    color: colors.primaryDark,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0.4,
    textTransform: "uppercase",
  },
  closeButton: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.pill,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  closeButtonText: {
    color: colors.textMuted,
    fontSize: 12,
    fontWeight: "800",
  },
  progressTrack: {
    flexDirection: "row",
    gap: spacing.xs,
  },
  progressSegment: {
    backgroundColor: colors.border,
    borderRadius: radius.pill,
    flex: 1,
    height: 5,
  },
  progressSegmentActive: {
    backgroundColor: colors.primary,
  },
  stepContent: {
    gap: spacing.sm,
    minHeight: 280,
  },
  stepLabel: {
    color: colors.primary,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.1,
  },
  stepTitle: {
    color: colors.text,
    fontSize: 21,
    fontWeight: "900",
    letterSpacing: -0.3,
    lineHeight: 27,
  },
  stepText: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 22,
  },
  contextCard: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.sm,
    gap: spacing.xs,
    padding: spacing.md,
  },
  contextLabel: {
    color: colors.primaryDark,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0.8,
  },
  contextTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
    lineHeight: 21,
  },
  contextText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  topicCard: {
    backgroundColor: colors.goldSoft,
    borderColor: "#EBCB91",
    borderRadius: radius.sm,
    borderWidth: 1,
    gap: spacing.xs,
    padding: spacing.md,
  },
  topicLabel: {
    color: colors.gold,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0.8,
  },
  topicTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "900",
  },
  topicText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  impactGrid: {
    gap: spacing.xs,
  },
  impactGridWide: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  impactRow: {
    alignItems: "center",
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    flexDirection: "row",
    gap: spacing.sm,
    justifyContent: "space-between",
    minHeight: 64,
    padding: spacing.sm,
  },
  impactRowWide: {
    width: "49%",
  },
  impactCopy: {
    flex: 1,
    gap: 2,
  },
  impactName: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "900",
  },
  impactEffect: {
    color: colors.textMuted,
    fontSize: 11,
    lineHeight: 16,
  },
  impactPercent: {
    color: colors.primaryDark,
    fontSize: 16,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
  },
  moreText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "800",
  },
  limitState: {
    backgroundColor: colors.surfaceMuted,
    borderLeftColor: colors.gold,
    borderLeftWidth: 3,
    borderRadius: radius.sm,
    padding: spacing.md,
  },
  limitStateText: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
  actions: {
    alignItems: "stretch",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    justifyContent: "flex-end",
  },
  primaryButton: {
    alignItems: "center",
    backgroundColor: colors.primary,
    borderRadius: radius.sm,
    flexDirection: "row",
    flexGrow: 1,
    gap: spacing.xs,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 190,
    paddingHorizontal: spacing.md,
  },
  primaryButtonText: {
    color: colors.white,
    fontSize: 13,
    fontWeight: "900",
    textAlign: "center",
  },
  buttonArrow: {
    color: colors.white,
    fontSize: 18,
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 92,
    paddingHorizontal: spacing.md,
  },
  secondaryButtonText: {
    color: colors.primary,
    fontSize: 13,
    fontWeight: "900",
  },
  scenarioActions: {
    flex: 1,
    gap: spacing.xs,
    minWidth: 190,
  },
  textButton: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.md,
  },
  textButtonText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: "800",
  },
  pressed: {
    opacity: 0.68,
  },
});
