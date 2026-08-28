import { ScrollView, StyleSheet, Text, View } from "react-native";

import { Eyebrow, SectionHeading, Surface } from "../components/Primitives";
import { colors, radius, spacing } from "../theme";

const steps = [
  { number: "01", title: "Sinal", text: "Focus, curva e mercado mostram uma mudança observável." },
  { number: "02", title: "Evidência", text: "Data, fonte e tamanho do movimento ficam perto da conclusão." },
  { number: "03", title: "Sua exposição", text: "A classe da posição filtra onde o sinal pode ser relevante." },
  { number: "04", title: "Limite", text: "A leitura termina dizendo o que ela não prova e o que pode mudá-la." },
] as const;

export function LearnScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.headerRow}>
        <View style={styles.headerCopy}>
          <Eyebrow>Sem economês</Eyebrow>
          <Text accessibilityRole="header" style={styles.title}>Entenda</Text>
        </View>
      </View>
      <View style={styles.hero}>
        <Eyebrow inverse>A lógica do FocusLens</Eyebrow>
        <Text style={styles.heroTitle}>Do mercado para a sua carteira, sem pular etapas</Text>
        <Text style={styles.heroSupport}>
          O app não começa pelo produto financeiro. Ele começa pela evidência,
          cruza a sua exposição e encerra com os limites da leitura.
        </Text>
      </View>
      <SectionHeading title="Como uma leitura nasce" />
      <View style={styles.timeline}>
        {steps.map((step, index) => (
          <View key={step.number} style={styles.stepRow}>
            <View style={styles.stepRail}>
              <View style={styles.stepNumber}><Text style={styles.stepNumberText}>{step.number}</Text></View>
              {index < steps.length - 1 ? <View style={styles.stepLine} /> : null}
            </View>
            <View style={styles.stepCopy}>
              <Text style={styles.stepTitle}>{step.title}</Text>
              <Text style={styles.stepText}>{step.text}</Text>
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
            O cruzamento é útil justamente porque as duas fontes podem divergir.
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
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { alignSelf: "center", boxSizing: "border-box", gap: spacing.lg, maxWidth: 820, paddingBottom: spacing.xl, paddingHorizontal: spacing.md, paddingTop: spacing.md, width: "100%" },
  headerRow: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  headerCopy: { gap: spacing.xxs },
  title: { color: colors.text, fontSize: 31, fontWeight: "900", letterSpacing: -1 },
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
  compareGrid: { flexDirection: "row", gap: spacing.sm },
  compareCard: { flex: 1, gap: spacing.xs, minHeight: 176 },
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
});
