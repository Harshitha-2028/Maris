import React, { useEffect, useState } from "react";
import { View, Text, FlatList, ScrollView } from "react-native";

// 👇 Replace with your backend URL + inject user wallet from auth/session
const API_URL = "http://<your-backend-ip>:8000";
const USER_WALLET = "0x1234..."; // get this from logged-in user

export default function UserDashboard() {
  const [myProjects, setMyProjects] = useState<any[]>([]);
  const [balances, setBalances] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMyData = async () => {
    setLoading(true);
    try {
      // 1. get projects where this user is participant/owner
      const res = await fetch(`${API_URL}/projects?owner=${USER_WALLET}`);
      const data = await res.json();
      setMyProjects(data);

      // 2. for each project, fetch balance
      const bal: Record<string, number> = {};
      for (const p of data) {
        const bRes = await fetch(`${API_URL}/balance/${USER_WALLET}/${p.project_id}`);
        const bData = await bRes.json();
        bal[p.project_id] = bData.balance;
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
    fetchMyData();
  }, []);

  return (
    <ScrollView className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold mb-4">User Dashboard</Text>

      {loading && <Text>Loading…</Text>}
      {error && <Text style={{ color: "red" }}>{error}</Text>}

      {/* user projects + balances */}
      <FlatList
        data={myProjects}
        keyExtractor={(item) => item.project_id}
        renderItem={({ item }) => (
          <View className="border rounded-lg p-3 mb-3">
            <Text className="font-semibold">{item.name || item.project_id}</Text>
            <Text className="text-xs text-gray-600">{item.project_type} • {item.location}</Text>

            <Text className="mt-1">My Balance: {balances[item.project_id] ?? 0} tCO₂e</Text>

            {/* data they submitted (from DB fields) */}
            <Text className="mt-2 font-medium">My Data</Text>
            <Text className="text-xs text-gray-700">
              Species: {item.tree_species || "N/A"}, Height: {item.tree_height || "–"} m,
              Biomass: {item.biomass_above_kg || 0}+{item.biomass_below_kg || 0} kg,
              SOC: {item.soil_organic_carbon_g_per_kg || "–"} g/kg
            </Text>

            {/* mentor/minter info (assuming backend adds this to project or tx logs) */}
            <Text className="mt-2 text-xs text-gray-500">
              Issued by: {item.issued_by?.name || item.minter_name || "Unknown"}
            </Text>
          </View>
        )}
      />

      {/* optional: aggregate chart of balances */}
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
