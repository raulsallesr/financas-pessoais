import liveSnapshotDocument from "./liveSnapshot.json";
import { selectMarketSnapshot } from "./snapshotProvider";

export const currentSnapshot = selectMarketSnapshot(liveSnapshotDocument);
