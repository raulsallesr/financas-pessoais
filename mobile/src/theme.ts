import { Platform } from "react-native";

export const colors = {
  background: "#F3F7F5",
  surface: "#FFFFFF",
  surfaceMuted: "#EAF2EF",
  text: "#17332F",
  textMuted: "#5E7470",
  primary: "#0F766E",
  primaryDark: "#0A514C",
  primarySoft: "#D9EEEA",
  gold: "#A16207",
  goldSoft: "#FFF2D7",
  border: "#D8E5E1",
  attention: "#B45309",
  attentionSoft: "#FEF3E3",
  positive: "#0F766E",
  positiveSoft: "#E2F3EE",
  neutral: "#536964",
  neutralSoft: "#EDF2F0",
  white: "#FFFFFF",
} as const;

export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 40,
} as const;

export const radius = {
  sm: 10,
  md: 16,
  lg: 24,
  pill: 999,
} as const;

export const shadow = Platform.select({
  web: {
    boxShadow: "0 8px 20px rgba(9, 47, 42, 0.08)",
  },
  default: {
    shadowColor: "#092F2A",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 3,
  },
})!;
