import { PublicMarketSnapshotV1 } from "./types";

export const PUBLIC_SNAPSHOT_HISTORY_SCHEMA_VERSION = 1 as const;
export const MAX_PUBLIC_SNAPSHOTS = 8;

export type PublicSnapshotHistoryV1 = {
  schemaVersion: typeof PUBLIC_SNAPSHOT_HISTORY_SCHEMA_VERSION;
  snapshots: readonly PublicMarketSnapshotV1[];
};

export type PublicSignalChange = {
  id: string;
  label: string;
  kind: "added" | "changed" | "removed";
  previousValue: string | null;
  currentValue: string | null;
};

export type PublicSnapshotComparison = {
  current: PublicMarketSnapshotV1;
  previous: PublicMarketSnapshotV1 | null;
  verdictChanged: boolean;
  signalChanges: readonly PublicSignalChange[];
};

export function createPublicSnapshotHistory(
  snapshots: readonly PublicMarketSnapshotV1[] = [],
): PublicSnapshotHistoryV1 {
  const unique = new Map<string, PublicMarketSnapshotV1>();
  for (const snapshot of snapshots) {
    if (!unique.has(snapshot.generatedAt)) {
      unique.set(snapshot.generatedAt, snapshot);
    }
  }
  return {
    schemaVersion: PUBLIC_SNAPSHOT_HISTORY_SCHEMA_VERSION,
    snapshots: [...unique.values()]
      .sort((left, right) => right.generatedAt.localeCompare(left.generatedAt))
      .slice(0, MAX_PUBLIC_SNAPSHOTS),
  };
}

export function recordPublicSnapshot(
  history: PublicSnapshotHistoryV1,
  snapshot: PublicMarketSnapshotV1,
): PublicSnapshotHistoryV1 {
  if (history.snapshots.some((item) => item.generatedAt === snapshot.generatedAt)) {
    return history;
  }
  return createPublicSnapshotHistory([snapshot, ...history.snapshots]);
}

export function comparePublicSnapshots(
  current: PublicMarketSnapshotV1,
  previous: PublicMarketSnapshotV1 | null,
): PublicSnapshotComparison {
  if (!previous) {
    return {
      current,
      previous: null,
      verdictChanged: false,
      signalChanges: [],
    };
  }

  const previousSignals = new Map(
    previous.signals.map((signal) => [signal.id, signal]),
  );
  const currentSignals = new Map(current.signals.map((signal) => [signal.id, signal]));
  const changed = current.signals.flatMap<PublicSignalChange>((signal) => {
    const before = previousSignals.get(signal.id);
    if (!before) {
      return [{
        id: signal.id,
        label: signal.label,
        kind: "added",
        previousValue: null,
        currentValue: signal.value,
      }];
    }
    if (
      before.value === signal.value &&
      before.change === signal.change &&
      before.headline === signal.headline &&
      before.tone === signal.tone
    ) {
      return [];
    }
    return [{
      id: signal.id,
      label: signal.label,
      kind: "changed",
      previousValue: before.value,
      currentValue: signal.value,
    }];
  });
  const removed = previous.signals.flatMap<PublicSignalChange>((signal) =>
    currentSignals.has(signal.id)
      ? []
      : [{
          id: signal.id,
          label: signal.label,
          kind: "removed",
          previousValue: signal.value,
          currentValue: null,
        }],
  );

  return {
    current,
    previous,
    verdictChanged: current.verdict !== previous.verdict,
    signalChanges: [...changed, ...removed],
  };
}
