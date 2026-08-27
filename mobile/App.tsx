import { useEffect, useState } from "react";
import {
  BackHandler,
  Platform,
  SafeAreaView,
  StatusBar as NativeStatusBar,
  StyleSheet,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";

import { BottomNav, TabKey } from "./src/components/BottomNav";
import { demoSnapshot } from "./src/data/demoSnapshot";
import { ALL_CLASSES, ClassFilter } from "./src/domain/insights";
import { LearnScreen } from "./src/screens/LearnScreen";
import { PortfolioScreen } from "./src/screens/PortfolioScreen";
import { ScenariosScreen } from "./src/screens/ScenariosScreen";
import { TodayScreen } from "./src/screens/TodayScreen";
import { colors } from "./src/theme";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("today");
  const [selectedSignalId, setSelectedSignalId] = useState(
    demoSnapshot.signals[0].id,
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
      return <PortfolioScreen snapshot={demoSnapshot} />;
    }
    if (activeTab === "scenarios") {
      return (
        <ScenariosScreen
          onShockChange={setShockBps}
          shockBps={shockBps}
          snapshot={demoSnapshot}
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
        snapshot={demoSnapshot}
      />
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View accessibilityLanguage="pt-BR" style={styles.app}>
        <View style={styles.screen}>{renderScreen()}</View>
        <BottomNav activeTab={activeTab} onChange={setActiveTab} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background,
    paddingTop:
      Platform.OS === "android" ? NativeStatusBar.currentHeight ?? 0 : 0,
  },
  app: {
    backgroundColor: colors.background,
    flex: 1,
  },
  screen: {
    flex: 1,
  },
});
