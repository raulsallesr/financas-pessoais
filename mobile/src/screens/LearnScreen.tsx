import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { Eyebrow, SectionHeading, Surface } from "../components/Primitives";
import {
  WeeklyReviewPanel,
  WeeklyReviewStep,
} from "../components/WeeklyReviewPanel";
import { signalById } from "../domain/insights";
import { PublicSnapshotHistoryV1 } from "../domain/snapshotHistory";
import { MarketSnapshot } from "../domain/types";
import testIds from "../testing/testIds.json";
import { colors, radius, spacing } from "../theme";

const steps = [
  { number: "01", title: "Sinal", text: "Focus, curva e mercado mostram uma mudança observável." },
  { number: "02", title: "Evidência", text: "Data, fonte e tamanho do movimento ficam perto da conclusão." },
  { number: "03", title: "Sua exposição", text: "A classe da posição filtra onde o sinal pode ser relevante." },
  { number: "04", title: "Limite", text: "A leitura termina dizendo o que ela não prova e o que pode mudá-la." },
] as const;

export function LearnScreen({
  favoriteSignalIds,
  onCancelReview,
  onExploreScenarios,
  onFinishReview,
  onStartReview,
  onStepChange,
  reviewSignalId,
  reviewStep,
  snapshot,
  snapshotHistory,
}: {
  favoriteSignalIds: readonly string[];
  onCancelReview: () => void;
  onExploreScenarios: () => void;
  onFinishReview: () => void;
  onStartReview: () => void;
  onStepChange: (step: WeeklyReviewStep) => void;
  reviewSignalId: string;
  reviewStep: WeeklyReviewStep | null;
  snapshot: MarketSnapshot;
  snapshotHistory: PublicSnapshotHistoryV1 | null;
}) {
  const [showMethod, setShowMethod] = useState(false);
  const signal = signalById(snapshot, reviewSignalId);
  const favorite = favoriteSignalIds.includes(reviewSignalId);

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      testID={testIds.screens.learn}
    >
      <View style={styles.headerRow}>
        <View style={styles.headerCopy}>
          <Eyebrow>Sem economês</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>Entenda</Text>
        </View>
      </View>

      {reviewStep === null ? (
        <Surface style={styles.reviewEntry}>
          <View style={styles.reviewTopline}>
            <Eyebrow>Revisão opcional da semana</Eyebrow>
            {favorite ? (
              <View style={styles.favoritePill}>
                <Text style={styles.favoriteText}>Acompanhando</Text>
              </View>
            ) : null}
          </View>
          <Text style={styles.reviewTitle}>Entenda a fotografia pelo seu recorte</Text>
          <Text style={styles.reviewSignal}>{signal.label} · {signal.value}</Text>
          <Text style={styles.reviewText}>
            Em cinco passos curtos, conecte mudança, evidência, carteira,
            Cenários e limite. Você pode sair quando quiser; nada é salvo.
          </Text>
          <Pressable
            accessibilityHint="Inicia uma sequência de cinco passos sem alterar a carteira"
            accessibilityRole="button"
            onPress={onStartReview}
            style={({ pressed }) => [styles.startButton, pressed && styles.pressed]}
            testID={testIds.weeklyReview.startFromLearn}
          >
            <Text style={styles.startButtonText}>Revisar {signal.label}</Text>
            <Text accessibilityElementsHidden style={styles.startArrow}>→</Text>
          </Pressable>
        </Surface>
      ) : (
        <WeeklyReviewPanel
          favorite={favorite}
          history={snapshotHistory}
          onCancel={onCancelReview}
          onExploreScenarios={onExploreScenarios}
          onFinish={onFinishReview}
          onStepChange={onStepChange}
          signalId={reviewSignalId}
          snapshot={snapshot}
          step={reviewStep}
        />
      )}

      <Pressable
        accessibilityHint="Mostra ou recolhe a explicação geral do método"
        accessibilityRole="button"
        accessibilityState={{ expanded: showMethod }}
        onPress={() => setShowMethod((current) => !current)}
        style={({ pressed }) => [styles.methodToggle, pressed && styles.pressed]}
      >
        <View style={styles.methodToggleCopy}>
          <Text style={styles.methodToggleLabel}>MÉTODO DE REFERÊNCIA</Text>
          <Text style={styles.methodToggleTitle}>
            {showMethod ? "Recolher como a leitura nasce" : "Ver como a leitura nasce"}
          </Text>
        </View>
        <Text accessibilityElementsHidden style={styles.methodToggleMark}>
          {showMethod ? "−" : "+"}
        </Text>
      </Pressable>

      {showMethod ? (
        <View style={styles.methodContent}>
          <View style={styles.hero}>
            <Eyebrow inverse>A lógica do FocusLens</Eyebrow>
            <Text style={styles.heroTitle}>Do mercado para a sua carteira, sem pular etapas</Text>
            <Text style={styles.heroSupport}>
              O app começa pela evidência, cruza a exposição e encerra com os
              limites da leitura — nunca pelo produto financeiro.
            </Text>
          </View>
          <SectionHeading title="Como uma leitura nasce" />
          <View style={styles.timeline}>
            {steps.map((item, index) => (
              <View key={item.number} style={styles.stepRow}>
                <View style={styles.stepRail}>
                  <View style={styles.stepNumber}><Text style={styles.stepNumberText}>{item.number}</Text></View>
                  {index < steps.length - 1 ? <View style={styles.stepLine} /> : null}
                </View>
                <View style={styles.stepCopy}>
                  <Text style={styles.stepTitle}>{item.title}</Text>
                  <Text style={styles.stepText}>{item.text}</Text>
                </View>
              </View>
            ))}
          </View>
          <SectionHeading title="Focus e curva não são a mesma coisa" />
          <View style={styles.compareGrid}>
            <Surface style={styles.compareCard}>
              <Text style={styles.compareLabel}>FOCUS</Text>
              <Text style={styles.compareTitle}>Expectativa declarada</Text>
              <Text style={styles.compareText}>
                Resume medianas informadas por participantes para indicadores e horizontes definidos.
              </Text>
            </Surface>
            <Surface style={styles.compareCard}>
              <Text style={styles.compareLabel}>CURVA</Text>
              <Text style={styles.compareTitle}>Preço negociado</Text>
              <Text style={styles.compareText}>
                Carrega expectativa, prêmio de prazo, liquidez, risco e condições do próprio título.
              </Text>
            </Surface>
          </View>
          <View style={styles.ruleCard}>
            <Text style={styles.ruleMark}>≠</Text>
            <View style={styles.ruleCopy}>
              <Text style={styles.ruleTitle}>Taxa de título não é previsão pura da Selic</Text>
              <Text style={styles.ruleText}>
                A divergência pede investigação; não vira ordem de ação.
              </Text>
            </View>
          </View>
          <SectionHeading title="O que este corte ainda não faz" />
          <Surface style={styles.limitCard}>
            {[
              "Não conecta conta bancária nem corretora.",
              "Não envia a carteira para nuvem; o cofre privado fica no aparelho.",
              "Não recomenda compra, venda ou alocação.",
              "Não estima retorno, probabilidade ou preço-alvo.",
            ].map((item) => (
              <View key={item} style={styles.limitRow}>
                <View style={styles.limitDash} />
                <Text style={styles.limitText}>{item}</Text>
              </View>
            ))}
          </Surface>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { alignSelf: "center", boxSizing: "border-box", gap: spacing.lg, maxWidth: 820, paddingBottom: spacing.xl, paddingHorizontal: spacing.md, paddingTop: spacing.md, width: "100%" },
  headerRow: { alignItems: "center", flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, justifyContent: "space-between" },
  headerCopy: { gap: spacing.xxs },
  title: { color: colors.text, fontSize: 31, fontWeight: "900", letterSpacing: -1 },
  reviewEntry: { backgroundColor: colors.primarySoft, gap: spacing.md },
  reviewTopline: { alignItems: "center", flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, justifyContent: "space-between" },
  favoritePill: { backgroundColor: colors.surface, borderRadius: radius.pill, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs },
  favoriteText: { color: colors.primaryDark, fontSize: 10, fontWeight: "900", letterSpacing: 0.4, textTransform: "uppercase" },
  reviewTitle: { color: colors.text, fontSize: 22, fontWeight: "900", letterSpacing: -0.4, lineHeight: 28 },
  reviewSignal: { color: colors.primaryDark, fontSize: 14, fontWeight: "900" },
  reviewText: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  startButton: { alignItems: "center", backgroundColor: colors.primary, borderRadius: radius.sm, flexDirection: "row", gap: spacing.xs, justifyContent: "center", minHeight: 48, paddingHorizontal: spacing.md },
  startButtonText: { color: colors.white, fontSize: 13, fontWeight: "900", textAlign: "center" },
  startArrow: { color: colors.white, fontSize: 18 },
  methodToggle: { alignItems: "center", backgroundColor: colors.surface, borderColor: colors.border, borderRadius: radius.md, borderWidth: 1, flexDirection: "row", gap: spacing.md, justifyContent: "space-between", minHeight: 64, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  methodToggleCopy: { flex: 1, gap: 3 },
  methodToggleLabel: { color: colors.textMuted, fontSize: 10, fontWeight: "900", letterSpacing: 0.7 },
  methodToggleTitle: { color: colors.text, fontSize: 14, fontWeight: "900" },
  methodToggleMark: { color: colors.primary, fontSize: 24, fontWeight: "700" },
  methodContent: { gap: spacing.lg },
  hero: { backgroundColor: colors.primaryDark, borderRadius: radius.lg, gap: spacing.sm, padding: spacing.lg },
  heroTitle: { color: colors.white, fontSize: 26, fontWeight: "900", letterSpacing: -0.7, lineHeight: 33 },
  heroSupport: { color: "#C9E8E2", fontSize: 14, lineHeight: 22 },
  timeline: { gap: 0 },
  stepRow: { flexDirection: "row", gap: spacing.md, minHeight: 94 },
  stepRail: { alignItems: "center", width: 46 },
  stepNumber: { alignItems: "center", backgroundColor: colors.primary, borderRadius: radius.pill, height: 42, justifyContent: "center", width: 42 },
  stepNumberText: { color: colors.white, fontSize: 11, fontVariant: ["tabular-nums"], fontWeight: "900" },
  stepLine: { backgroundColor: colors.border, flex: 1, width: 2 },
  stepCopy: { flex: 1, gap: 4, paddingBottom: spacing.lg, paddingTop: spacing.xs },
  stepTitle: { color: colors.text, fontSize: 17, fontWeight: "900" },
  stepText: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  compareGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  compareCard: { flex: 1, gap: spacing.xs, minHeight: 176, minWidth: 220 },
  compareLabel: { color: colors.gold, fontSize: 10, fontWeight: "900", letterSpacing: 1.2 },
  compareTitle: { color: colors.text, fontSize: 16, fontWeight: "900", lineHeight: 21 },
  compareText: { color: colors.textMuted, fontSize: 12, lineHeight: 19 },
  ruleCard: { alignItems: "center", backgroundColor: colors.goldSoft, borderColor: "#EBCB91", borderRadius: radius.md, borderWidth: 1, flexDirection: "row", gap: spacing.md, padding: spacing.md },
  ruleMark: { color: colors.gold, fontSize: 32, fontWeight: "900" },
  ruleCopy: { flex: 1, gap: 4 },
  ruleTitle: { color: colors.text, fontSize: 15, fontWeight: "900", lineHeight: 20 },
  ruleText: { color: colors.textMuted, fontSize: 12, lineHeight: 19 },
  limitCard: { gap: spacing.sm },
  limitRow: { alignItems: "flex-start", flexDirection: "row", gap: spacing.sm },
  limitDash: { backgroundColor: colors.gold, borderRadius: 2, height: 3, marginTop: 8, width: 12 },
  limitText: { color: colors.textMuted, flex: 1, fontSize: 13, lineHeight: 20 },
  pressed: { opacity: 0.68 },
});
