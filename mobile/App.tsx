import { useEffect, useState } from "react";
import {
  BackHandler,
  Platform,
  StyleSheet,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import {
  initialWindowMetrics,
  SafeAreaProvider,
  SafeAreaView,
} from "react-native-safe-area-context";

import { BottomNav, TabKey } from "./src/components/BottomNav";
import { currentSnapshot } from "./src/data/currentSnapshot";
import { ALL_CLASSES, ClassFilter } from "./src/domain/insights";
import { LearnScreen } from "./src/screens/LearnScreen";
import { PortfolioScreen } from "./src/screens/PortfolioScreen";
import { ScenariosScreen } from "./src/screens/ScenariosScreen";
import { TodayScreen } from "./src/screens/TodayScreen";
import { colors } from "./src/theme";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("today");
  const [selectedSignalId, setSelectedSignalId] = useState(
    currentSnapshot.signals[0].id,
  );
  const [classFilter, setClassFilter] = useState<ClassFilter>(ALL_CLASSES);
  const [shockBps, setShockBps] = useState(0);

  useEffect(() => {
    if (Platform.OS !== "android") {
      return undefined;
    }
    const subscription = BackHandler.addEventListener(
      "hardwareBackPress",
      () => {
        if (activeTab === "today") {
          return false;
        }
        setActiveTab("today");
        return true;
      },
    );
    return () => subscription.remove();
  }, [activeTab]);

  const renderScreen = () => {
    if (activeTab === "portfolio") {
      return <PortfolioScreen snapshot={currentSnapshot} />;
    }
    if (activeTab === "scenarios") {
      return (
        <ScenariosScreen
          onShockChange={setShockBps}
          shockBps={shockBps}
          snapshot={currentSnapshot}
        />
      );
    }
    if (activeTab === "learn") {
      return <LearnScreen />;
    }
    return (
      <TodayScreen
        classFilter={classFilter}
        onClassFilter={setClassFilter}
        onNavigate={setActiveTab}
        onSelectSignal={setSelectedSignalId}
        selectedSignalId={selectedSignalId}
        snapshot={currentSnapshot}
      />
    );
  };

  return (
    <SafeAreaProvider initialMetrics={initialWindowMetrics}>
      <SafeAreaView
        edges={["top", "right", "bottom", "left"]}
        style={styles.safeArea}
      >
        <StatusBar style="dark" />
        <View accessibilityLanguage="pt-BR" style={styles.app}>
          <View style={styles.screen}>{renderScreen()}</View>
          <BottomNav activeTab={activeTab} onChange={setActiveTab} />
        </View>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background,
  },
  app: {
    backgroundColor: colors.background,
    flex: 1,
  },
  screen: {
    flex: 1,
  },
});
