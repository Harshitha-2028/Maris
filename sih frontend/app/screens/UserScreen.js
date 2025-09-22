import React, { useEffect, useState } from "react";
import { View, Text, FlatList, ScrollView } from "react-native";
import { LineChart } from "react-native-chart-kit";
import Constants from "expo-constants";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = Constants.expoConfig?.extra?.API_URL ?? "http://10.0.2.2:8000";

export default function UserDashboard() {
  const [userWallet, setUserWallet] = useState(null);
  const [myProjects, setMyProjects] = useState([]);
  const [balances, setBalances] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMyData = async (wallet) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/projects?owner=${wallet}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : [];
      setMyProjects(list);

      const bal = {};
      for (const p of list) {
        const bRes = await fetch(`${API_URL}/balance/${wallet}/${p.project_id}`);
        const bData = await bRes.json();
        bal[p.project_id] = Number(bData?.balance ?? 0);
      }
      setBalances(bal);
    } catch (err) {
      console.error("Failed to fetch user data:", err);
      setError("Failed to fetch");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem("user");
        if (raw) {
          const u = JSON.parse(raw);
          // if your backend returns/stores wallet, keep it here; else hardcode for now
          const wallet = u?.wallet || "0x1234...";
          setUserWallet(wallet);
          fetchMyData(wallet);
        }
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  return (
    <ScrollView className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold mb-4">User Dashboard</Text>

      {loading && <Text>Loading…</Text>}
      {error && <Text style={{ color: "red" }}>{error}</Text>}

      <FlatList
        data={myProjects}
        keyExtractor={(item) => item.project_id}
        renderItem={({ item }) => (
          <View className="border rounded-lg p-3 mb-3">
            <Text className="font-semibold">{item.name || item.project_id}</Text>
            <Text className="text-xs text-gray-600">{item.project_type} • {item.location}</Text>
            <Text className="mt-1">My Balance: {balances[item.project_id] ?? 0} tCO₂e</Text>
            <Text className="mt-2 font-medium">My Data</Text>
            <Text className="text-xs text-gray-700">
              Species: {item.tree_species || "N/A"}, Height: {item.tree_height || "–"} m,
              Biomass: {(item.biomass_above_kg || 0) + (item.biomass_below_kg || 0)} kg,
              SOC: {item.soil_organic_carbon_g_per_kg || "–"} g/kg
            </Text>
            <Text className="mt-2 text-xs text-gray-500">
              Issued by: {item.issued_by?.name || item.minter_name || "Unknown"}
            </Text>
          </View>
        )}
      />

      {Object.keys(balances).length > 0 && (
        <View className="mt-6 border rounded-lg p-3">
          <Text className="font-semibold mb-2">Credits by Project</Text>
          <LineChart
            data={{
              labels: Object.keys(balances),
              datasets: [{ data: Object.values(balances).map((v) => Number(v)), color: () => "#4CAF50" }],
            }}
            width={320}
            height={200}
            chartConfig={{
              backgroundColor: "#ffffff",
              backgroundGradientFrom: "#ffffff",
              backgroundGradientTo: "#ffffff",
              color: () => "#4CAF50",
              labelColor: () => "#000",
              decimalPlaces: 0,
            }}
          />
        </View>
      )}
    </ScrollView>
  );
}
