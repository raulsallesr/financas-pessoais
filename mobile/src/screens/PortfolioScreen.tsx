import { randomUUID } from "expo-crypto";
import { useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  DemoPill,
  Eyebrow,
  formatCurrency,
  SectionHeading,
  Surface,
} from "../components/Primitives";
import { allocationPercent, portfolioTotal } from "../domain/insights";
import {
  ASSET_CLASSES,
  buildPositionFromDraft,
  MAX_PORTFOLIO_POSITIONS,
  PositionDraft,
  PositionDraftErrors,
} from "../domain/privatePortfolio";
import { MarketSnapshot, Position } from "../domain/types";
import { colors, radius, spacing } from "../theme";

export type PortfolioMode =
  | "loading"
  | "demo"
  | "local"
  | "unavailable"
  | "error";

type PortfolioScreenProps = {
  mode: PortfolioMode;
  snapshot: MarketSnapshot;
  storageMessage?: string;
  onSavePositions: (positions: readonly Position[]) => Promise<void>;
  onReset: () => Promise<void>;
};

const EMPTY_DRAFT: PositionDraft = {
  name: "",
  assetClass: null,
  amountText: "",
};

function portfolioSupport(mode: PortfolioMode, count: number): string {
  if (mode === "local") {
    return `${count} ${count === 1 ? "posição" : "posições"} · cofre criptografado neste aparelho`;
  }
  if (mode === "loading") {
    return "Verificando o cofre local deste aparelho…";
  }
  if (mode === "error") {
    return "A carteira privada não foi aberta; nenhum dado fictício foi misturado.";
  }
  return `${count} ${count === 1 ? "posição fictícia" : "posições fictícias"} · demonstração local`;
}

function PortfolioPill({ mode }: { mode: PortfolioMode }) {
  if (mode === "local") {
    return (
      <View accessibilityLabel="Carteira somente neste aparelho" style={styles.localPill}>
        <View style={styles.localDot} />
        <Text style={styles.localPillText}>SÓ NO APARELHO</Text>
      </View>
    );
  }
  if (mode === "error") {
    return (
      <View accessibilityLabel="Cofre local bloqueado" style={styles.errorPill}>
        <View style={styles.errorDot} />
        <Text style={styles.errorPillText}>COFRE BLOQUEADO</Text>
      </View>
    );
  }
  return <DemoPill />;
}

export function PortfolioScreen({
  mode,
  snapshot,
  storageMessage,
  onSavePositions,
  onReset,
}: PortfolioScreenProps) {
  const [hidden, setHidden] = useState(false);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<PositionDraft>(EMPTY_DRAFT);
  const [errors, setErrors] = useState<PositionDraftErrors>({});
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const total = portfolioTotal(snapshot);
  const sorted = [...snapshot.positions].sort((a, b) => b.amount - a.amount);
  const canEdit = mode === "demo" || mode === "local";

  function openNewPosition() {
    setEditingId(null);
    setDraft(EMPTY_DRAFT);
    setErrors({});
    setActionError(null);
    setFeedback(null);
    setEditorOpen(true);
  }

  function openExistingPosition(position: Position) {
    setEditingId(position.id);
    setDraft({
      name: position.name,
      assetClass: position.assetClass,
      amountText: position.amount.toFixed(2).replace(".", ","),
    });
    setErrors({});
    setActionError(null);
    setFeedback(null);
    setEditorOpen(true);
  }

  function closeEditor() {
    if (saving) {
      return;
    }
    setEditorOpen(false);
    setEditingId(null);
    setErrors({});
    setActionError(null);
  }

  function setDraftField<Key extends keyof PositionDraft>(
    key: Key,
    value: PositionDraft[Key],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined }));
    setActionError(null);
    setFeedback(null);
  }

  function validateField(field: keyof PositionDraft) {
    const result = buildPositionFromDraft(draft, editingId ?? "draft-position");
    setErrors((current) => ({
      ...current,
      [field]: result.ok ? undefined : result.errors[field],
    }));
  }

  async function saveDraft() {
    if (
      !editingId &&
      mode === "local" &&
      snapshot.positions.length >= MAX_PORTFOLIO_POSITIONS
    ) {
      setActionError(`A carteira aceita até ${MAX_PORTFOLIO_POSITIONS} posições.`);
      return;
    }

    const positionId = editingId ?? `local-${randomUUID()}`;
    const result = buildPositionFromDraft(draft, positionId);
    if (!result.ok) {
      setErrors(result.errors);
      setActionError("Revise os campos destacados antes de salvar.");
      return;
    }

    const positions = editingId
      ? snapshot.positions.map((position) =>
          position.id === editingId ? result.position : position,
        )
      : mode === "local"
        ? [...snapshot.positions, result.position]
        : [result.position];

    setSaving(true);
    setActionError(null);
    try {
      await onSavePositions(positions);
      setEditorOpen(false);
      setEditingId(null);
      setDraft(EMPTY_DRAFT);
      setErrors({});
      setFeedback(
        editingId
          ? "Posição atualizada no cofre local."
          : "Posição salva no cofre local.",
      );
    } catch {
      setActionError(
        "Não foi possível salvar no cofre. A carteira anterior foi preservada.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function removePosition(position: Position) {
    if (saving) {
      return;
    }
    setSaving(true);
    setActionError(null);
    setFeedback(null);
    try {
      await onSavePositions(
        snapshot.positions.filter((item) => item.id !== position.id),
      );
      setFeedback(`${position.shortName} foi removido da carteira local.`);
    } catch {
      setActionError("Não foi possível excluir a posição. A carteira foi preservada.");
    } finally {
      setSaving(false);
    }
  }

  function confirmRemove(position: Position) {
    Alert.alert(
      "Excluir posição?",
      `${position.shortName} será removido somente deste aparelho.`,
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Excluir",
          style: "destructive",
          onPress: () => void removePosition(position),
        },
      ],
    );
  }

  async function resetLocalPortfolio() {
    if (saving) {
      return;
    }
    setSaving(true);
    setActionError(null);
    setFeedback(null);
    try {
      await onReset();
      setEditorOpen(false);
      setFeedback(
        "Carteira local apagada. A demonstração fictícia voltou a ser exibida.",
      );
    } catch {
      setActionError("Não foi possível apagar o cofre local. Tente novamente.");
    } finally {
      setSaving(false);
    }
  }

  function confirmReset() {
    Alert.alert(
      mode === "error" ? "Apagar cofre inacessível?" : "Apagar carteira local?",
      "O arquivo criptografado e a chave deste aparelho serão removidos. Esta ação não pode ser desfeita.",
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Apagar",
          style: "destructive",
          onPress: () => void resetLocalPortfolio(),
        },
      ],
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.keyboardArea}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.headerRow}>
          <View style={styles.headerCopy}>
            <Eyebrow>Sua fotografia</Eyebrow>
            <Text accessibilityRole="header" style={styles.title}>
              Carteira
            </Text>
          </View>
          <PortfolioPill mode={mode} />
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
            {portfolioSupport(mode, snapshot.positions.length)}
          </Text>
        </View>

        {storageMessage ? (
          <View
            accessibilityLiveRegion="polite"
            style={[styles.statusCard, mode === "error" && styles.statusCardError]}
          >
            <Text style={styles.statusTitle}>
              {mode === "error"
                ? "O cofre falhou de forma segura"
                : "Cofre nativo indisponível aqui"}
            </Text>
            <Text style={styles.statusSupport}>{storageMessage}</Text>
            {mode === "error" ? (
              <Pressable
                accessibilityRole="button"
                disabled={saving}
                onPress={confirmReset}
                style={({ pressed }) => [
                  styles.dangerButton,
                  pressed && styles.pressed,
                  saving && styles.disabled,
                ]}
              >
                <Text style={styles.dangerButtonText}>Apagar e recomeçar</Text>
              </Pressable>
            ) : null}
          </View>
        ) : null}

        {canEdit ? (
          <Pressable
            accessibilityHint="Abre o formulário de uma posição"
            accessibilityRole="button"
            disabled={saving}
            onPress={openNewPosition}
            style={({ pressed }) => [
              styles.primaryButton,
              pressed && styles.primaryButtonPressed,
              saving && styles.disabled,
            ]}
          >
            <Text style={styles.primaryButtonText}>
              {mode === "local" ? "Adicionar posição" : "Criar carteira local"}
            </Text>
          </Pressable>
        ) : null}

        {editorOpen ? (
          <Surface style={styles.editorCard}>
            <View style={styles.editorHeading}>
              <View style={styles.editorHeadingCopy}>
                <Eyebrow>{editingId ? "Editar posição" : "Nova posição"}</Eyebrow>
                <Text accessibilityRole="header" style={styles.editorTitle}>
                  {editingId ? "Atualize os dados" : "Inclua um ativo"}
                </Text>
              </View>
              <Pressable
                accessibilityLabel="Fechar editor de posição"
                accessibilityRole="button"
                disabled={saving}
                onPress={closeEditor}
                style={({ pressed }) => [
                  styles.closeButton,
                  pressed && styles.pressed,
                ]}
              >
                <Text style={styles.closeButtonText}>Fechar</Text>
              </Pressable>
            </View>

            {mode === "demo" ? (
              <Text style={styles.editorNotice}>
                Ao salvar, a carteira fictícia sai de cena e somente esta posição passa a compor sua fotografia local.
              </Text>
            ) : null}

            <View style={styles.fieldGroup}>
              <Text style={styles.fieldLabel}>Nome do ativo</Text>
              <TextInput
                accessibilityHint="Use um nome que você reconheça na carteira"
                accessibilityLabel="Nome do ativo"
                autoCapitalize="words"
                editable={!saving}
                maxLength={80}
                onBlur={() => validateField("name")}
                onChangeText={(value) => setDraftField("name", value)}
                placeholder="Ex.: Tesouro Selic 2029"
                placeholderTextColor={colors.textMuted}
                returnKeyType="next"
                style={[styles.input, errors.name && styles.inputError]}
                value={draft.name}
              />
              {errors.name ? (
                <Text accessibilityLiveRegion="polite" style={styles.errorText}>
                  {errors.name}
                </Text>
              ) : null}
            </View>

            <View style={styles.fieldGroup}>
              <Text style={styles.fieldLabel}>Classe do ativo</Text>
              <Text style={styles.fieldHelper}>
                A classe conecta a posição aos sinais públicos; ela não avalia a qualidade do investimento.
              </Text>
              <View accessibilityRole="radiogroup" style={styles.classGrid}>
                {ASSET_CLASSES.map((assetClass) => {
                  const selected = draft.assetClass === assetClass;
                  return (
                    <Pressable
                      accessibilityLabel={assetClass}
                      accessibilityRole="radio"
                      accessibilityState={{ selected }}
                      disabled={saving}
                      key={assetClass}
                      onPress={() => setDraftField("assetClass", assetClass)}
                      style={({ pressed }) => [
                        styles.classOption,
                        selected && styles.classOptionSelected,
                        pressed && styles.pressed,
                      ]}
                    >
                      <View
                        style={[styles.classDot, selected && styles.classDotSelected]}
                      />
                      <Text
                        style={[
                          styles.classOptionText,
                          selected && styles.classOptionTextSelected,
                        ]}
                      >
                        {assetClass}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
              {errors.assetClass ? (
                <Text accessibilityLiveRegion="polite" style={styles.errorText}>
                  {errors.assetClass}
                </Text>
              ) : null}
            </View>

            <View style={styles.fieldGroup}>
              <Text style={styles.fieldLabel}>Valor atual em reais</Text>
              <TextInput
                accessibilityHint="Aceita formatos como 1250,50 ou 1.250,50"
                accessibilityLabel="Valor atual em reais"
                editable={!saving}
                inputMode="decimal"
                keyboardType={Platform.OS === "ios" ? "decimal-pad" : "numeric"}
                onBlur={() => validateField("amountText")}
                onChangeText={(value) => setDraftField("amountText", value)}
                placeholder="Ex.: 1.250,50"
                placeholderTextColor={colors.textMuted}
                returnKeyType="done"
                style={[styles.input, errors.amountText && styles.inputError]}
                value={draft.amountText}
              />
              {errors.amountText ? (
                <Text accessibilityLiveRegion="polite" style={styles.errorText}>
                  {errors.amountText}
                </Text>
              ) : null}
            </View>

            {actionError ? (
              <Text accessibilityLiveRegion="assertive" style={styles.formError}>
                {actionError}
              </Text>
            ) : null}

            <View style={styles.editorActions}>
              <Pressable
                accessibilityRole="button"
                disabled={saving}
                onPress={() => void saveDraft()}
                style={({ pressed }) => [
                  styles.primaryButton,
                  pressed && styles.primaryButtonPressed,
                  saving && styles.disabled,
                ]}
              >
                <Text style={styles.primaryButtonText}>
                  {saving ? "Salvando no cofre…" : "Salvar no aparelho"}
                </Text>
              </Pressable>
              <Pressable
                accessibilityRole="button"
                disabled={saving}
                onPress={closeEditor}
                style={({ pressed }) => [
                  styles.secondaryButton,
                  pressed && styles.pressed,
                ]}
              >
                <Text style={styles.secondaryButtonText}>Cancelar</Text>
              </Pressable>
            </View>
          </Surface>
        ) : null}

        {feedback ? (
          <Text accessibilityLiveRegion="polite" style={styles.feedbackText}>
            {feedback}
          </Text>
        ) : null}
        {!editorOpen && actionError ? (
          <Text accessibilityLiveRegion="assertive" style={styles.formError}>
            {actionError}
          </Text>
        ) : null}

        <SectionHeading
          title="Onde você está exposto"
          support="A barra mostra peso, não qualidade nem recomendação."
        />
        <Surface style={styles.allocationCard}>
          {sorted.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyTitle}>Nenhuma posição disponível</Text>
              <Text style={styles.emptySupport}>
                {mode === "error"
                  ? "Reinicie o cofre para montar uma nova carteira local."
                  : "Adicione a primeira posição para conectar sua carteira aos sinais públicos."}
              </Text>
            </View>
          ) : (
            sorted.map((position) => {
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
                    accessibilityLabel={`${position.shortName}: ${allocation.toFixed(1)}% da carteira`}
                    style={styles.track}
                  >
                    <View style={[styles.bar, { width: `${allocation}%` }]} />
                  </View>
                  {mode === "local" ? (
                    <View style={styles.positionActions}>
                      <Pressable
                        accessibilityLabel={`Editar ${position.shortName}`}
                        accessibilityRole="button"
                        disabled={saving}
                        onPress={() => openExistingPosition(position)}
                        style={({ pressed }) => [
                          styles.smallButton,
                          pressed && styles.pressed,
                          saving && styles.disabled,
                        ]}
                      >
                        <Text style={styles.smallButtonText}>Editar</Text>
                      </Pressable>
                      <Pressable
                        accessibilityLabel={`Excluir ${position.shortName}`}
                        accessibilityRole="button"
                        disabled={saving}
                        onPress={() => confirmRemove(position)}
                        style={({ pressed }) => [
                          styles.smallDangerButton,
                          pressed && styles.pressed,
                          saving && styles.disabled,
                        ]}
                      >
                        <Text style={styles.smallDangerText}>Excluir</Text>
                      </Pressable>
                    </View>
                  ) : null}
                </View>
              );
            })
          )}
        </Surface>

        <SectionHeading title="Privacidade desde o começo" />
        <View style={styles.privacyCard}>
          <View accessibilityElementsHidden style={styles.lockMark}>
            <View style={styles.lockArc} />
            <View style={styles.lockBody} />
          </View>
          <View style={styles.privacyCopy}>
            <Text style={styles.privacyTitle}>Carteira local por padrão</Text>
            <Text style={styles.privacySupport}>
              {mode === "local"
                ? "A chave fica no cofre nativo do sistema e a carteira em um arquivo AES-GCM autenticado. Não há envio para nuvem, EAS ou snapshot público."
                : "A demonstração não contém dados pessoais. Ao criar sua carteira no Android ou iOS, ela fica criptografada e restrita ao aparelho."}
            </Text>
          </View>
        </View>

        {mode === "local" ? (
          <Pressable
            accessibilityRole="button"
            disabled={saving}
            onPress={confirmReset}
            style={({ pressed }) => [
              styles.resetButton,
              pressed && styles.pressed,
              saving && styles.disabled,
            ]}
          >
            <Text style={styles.resetButtonText}>Apagar carteira local</Text>
          </Pressable>
        ) : null}

        <Surface style={styles.nextCard}>
          <Eyebrow>Próximo incremento</Eyebrow>
          <Text style={styles.nextTitle}>Importação B3 sanitizada</Text>
          <Text style={styles.nextSupport}>
            O editor seguro é a base. A próxima entrega importa um arquivo escolhido pelo usuário, valida somente os campos necessários e descarta o original após o processamento local.
          </Text>
        </Surface>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  keyboardArea: { flex: 1 },
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
  headerCopy: { gap: spacing.xxs },
  title: {
    color: colors.text,
    fontSize: 31,
    fontWeight: "900",
    letterSpacing: -1,
  },
  localPill: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  localDot: {
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
    height: 6,
    width: 6,
  },
  localPillText: {
    color: colors.primaryDark,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
  },
  errorPill: {
    alignItems: "center",
    backgroundColor: colors.dangerSoft,
    borderRadius: radius.pill,
    flexDirection: "row",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  errorDot: {
    backgroundColor: colors.danger,
    borderRadius: radius.pill,
    height: 6,
    width: 6,
  },
  errorPillText: {
    color: colors.danger,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.7,
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
  balanceLabel: { color: "#C9E8E2", fontSize: 12, fontWeight: "700" },
  balanceValue: {
    color: colors.white,
    fontSize: 34,
    fontVariant: ["tabular-nums"],
    fontWeight: "900",
    letterSpacing: -1,
  },
  balanceSupport: { color: "#A9D2CA", fontSize: 12, lineHeight: 18 },
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
  privacyDotHidden: { backgroundColor: "#F8CF8B" },
  privacyText: { color: colors.white, fontSize: 11, fontWeight: "700" },
  statusCard: {
    backgroundColor: colors.goldSoft,
    borderColor: colors.gold,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.xs,
    padding: spacing.md,
  },
  statusCardError: {
    backgroundColor: colors.dangerSoft,
    borderColor: colors.danger,
  },
  statusTitle: { color: colors.text, fontSize: 15, fontWeight: "900" },
  statusSupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  primaryButton: {
    alignItems: "center",
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    justifyContent: "center",
    minHeight: 52,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  primaryButtonPressed: { backgroundColor: colors.primaryDark },
  primaryButtonText: {
    color: colors.white,
    fontSize: 15,
    fontWeight: "800",
    textAlign: "center",
  },
  secondaryButton: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 52,
    paddingHorizontal: spacing.md,
  },
  secondaryButtonText: { color: colors.text, fontSize: 14, fontWeight: "800" },
  editorCard: { gap: spacing.lg },
  editorHeading: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  editorHeadingCopy: { flex: 1, gap: spacing.xxs, minWidth: 190 },
  editorTitle: { color: colors.text, fontSize: 20, fontWeight: "900" },
  closeButton: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
    minWidth: 64,
    paddingHorizontal: spacing.sm,
  },
  closeButtonText: { color: colors.primary, fontSize: 13, fontWeight: "800" },
  editorNotice: {
    backgroundColor: colors.primarySoft,
    borderRadius: radius.sm,
    color: colors.primaryDark,
    fontSize: 13,
    lineHeight: 20,
    padding: spacing.sm,
  },
  fieldGroup: { gap: spacing.xs },
  fieldLabel: { color: colors.text, fontSize: 14, fontWeight: "800" },
  fieldHelper: { color: colors.textMuted, fontSize: 12, lineHeight: 18 },
  input: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.text,
    fontSize: 16,
    minHeight: 52,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
  },
  inputError: { borderColor: colors.danger, borderWidth: 2 },
  classGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  classOption: {
    alignItems: "center",
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    flexDirection: "row",
    gap: spacing.xs,
    minHeight: 48,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  classOptionSelected: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primary,
    borderWidth: 2,
  },
  classDot: {
    borderColor: colors.textMuted,
    borderRadius: radius.pill,
    borderWidth: 1,
    height: 12,
    width: 12,
  },
  classDotSelected: { backgroundColor: colors.primary, borderColor: colors.primary },
  classOptionText: {
    color: colors.textMuted,
    flexShrink: 1,
    fontSize: 12,
    fontWeight: "700",
  },
  classOptionTextSelected: { color: colors.primaryDark },
  errorText: {
    color: colors.danger,
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 18,
  },
  formError: {
    backgroundColor: colors.dangerSoft,
    borderRadius: radius.sm,
    color: colors.danger,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 20,
    padding: spacing.sm,
  },
  feedbackText: {
    backgroundColor: colors.positiveSoft,
    borderRadius: radius.sm,
    color: colors.primaryDark,
    fontSize: 13,
    fontWeight: "700",
    lineHeight: 20,
    padding: spacing.sm,
  },
  editorActions: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  disabled: { opacity: 0.45 },
  dangerButton: {
    alignItems: "center",
    alignSelf: "flex-start",
    borderColor: colors.danger,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.sm,
  },
  dangerButtonText: { color: colors.danger, fontSize: 13, fontWeight: "800" },
  allocationCard: { gap: spacing.lg },
  allocationRow: { gap: spacing.xs },
  allocationTopline: {
    alignItems: "flex-start",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    justifyContent: "space-between",
  },
  positionCopy: { flex: 1, gap: 2, minWidth: 150 },
  positionName: { color: colors.text, fontSize: 15, fontWeight: "800" },
  positionClass: { color: colors.textMuted, fontSize: 11 },
  positionValue: { alignItems: "flex-end" },
  positionAmount: {
    color: colors.text,
    fontSize: 13,
    fontVariant: ["tabular-nums"],
    fontWeight: "700",
  },
  positionPercent: { color: colors.primary, fontSize: 11, fontWeight: "800" },
  track: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.pill,
    height: 8,
    overflow: "hidden",
  },
  bar: { backgroundColor: colors.primary, borderRadius: radius.pill, height: "100%" },
  positionActions: { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  smallButton: {
    alignItems: "center",
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 72,
    paddingHorizontal: spacing.sm,
  },
  smallButtonText: { color: colors.primary, fontSize: 12, fontWeight: "800" },
  smallDangerButton: {
    alignItems: "center",
    borderColor: colors.dangerSoft,
    borderRadius: radius.sm,
    borderWidth: 1,
    justifyContent: "center",
    minHeight: 48,
    minWidth: 72,
    paddingHorizontal: spacing.sm,
  },
  smallDangerText: { color: colors.danger, fontSize: 12, fontWeight: "800" },
  emptyState: { gap: spacing.xs, paddingVertical: spacing.sm },
  emptyTitle: { color: colors.text, fontSize: 15, fontWeight: "900" },
  emptySupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  privacyCard: {
    alignItems: "center",
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    flexDirection: "row",
    flexWrap: "wrap",
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
  privacyCopy: { flex: 1, gap: spacing.xxs, minWidth: 220 },
  privacyTitle: { color: colors.primaryDark, fontSize: 16, fontWeight: "900" },
  privacySupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  resetButton: {
    alignItems: "center",
    alignSelf: "flex-start",
    justifyContent: "center",
    minHeight: 48,
    paddingHorizontal: spacing.sm,
  },
  resetButtonText: { color: colors.danger, fontSize: 13, fontWeight: "800" },
  nextCard: { gap: spacing.xs },
  nextTitle: { color: colors.text, fontSize: 18, fontWeight: "900" },
  nextSupport: { color: colors.textMuted, fontSize: 13, lineHeight: 20 },
  pressed: { opacity: 0.65 },
});
