import liveSnapshotDocument from "./liveSnapshot.json";
import { selectMarketSnapshot, validateLiveSnapshot } from "./snapshotProvider";

export const currentPublicSnapshot = validateLiveSnapshot(liveSnapshotDocument)
  ? liveSnapshotDocument
  : null;
export const currentSnapshot = selectMarketSnapshot(liveSnapshotDocument);
