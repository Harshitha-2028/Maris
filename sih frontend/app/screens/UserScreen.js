
  

import { View, Text, FlatList } from "react-native";
import { LineChart } from "react-native-chart-kit";
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

// 👇 Replace with your backend URL (e.g., http://10.0.2.2:5000 for Android emulator)
const API_URL = "http://<your-backend-ip>:5000";

export default function UserDashboard() {
  const { t } = useTranslation();
  const [credits, setCredits] = useState([]);

  // Fetch credits from backend
  const fetchCredits = async () => {
    try {
      const res = await fetch(`${API_URL}/credits`);
      const data = await res.json();
      setCredits(data);
    } catch (err) {
      console.error("Failed to fetch credits:", err);
    }
  };

  useEffect(() => {
    fetchCredits();
  }, []);

  return (
    <View className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold">{t("user_dashboard")}</Text>

      <FlatList
        data={credits}
        renderItem={({ item }) => (
          <Text>{item.tokenId}: {item.amount} tCO2e ({item.status})</Text>
        )}
        keyExtractor={(item, index) => item.tokenId ?? index.toString()}
      />

      <LineChart
        data={{
          labels: ["Mangrove", "Reforestation", "Urban Forestry", "Solar/Wind", "Others"],
          datasets: [{ data: [13000, 19200, 8400, 21450, 10750], color: () => "#4CAF50" }],
        }}
        width={300}
        height={200}
        chartConfig={{
          backgroundColor: "#ffffff",
          backgroundGradientFrom: "#ffffff",
          backgroundGradientTo: "#ffffff",
          color: () => "#4CAF50",
          labelColor: () => "#000000",
        }}
        bezier
      />
    </View>
  );
}
