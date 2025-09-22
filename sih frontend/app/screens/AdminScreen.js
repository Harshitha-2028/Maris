
  

import { View, Text, FlatList, TextInput, Button } from "react-native";
import { LineChart } from "react-native-chart-kit";
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

// 👇 Replace with your backend URL (local: http://10.0.2.2:5000 for Android emulator)
const API_URL = "http://<your-backend-ip>:5000";

export default function AdminDashboard() {
  const { t } = useTranslation();

  const [projects, setProjects] = useState([]);
  const [projectId, setProjectId] = useState("");
  const [metadataCID, setMetadataCID] = useState("");

  // Fetch projects from backend
  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/projects`);
      const data = await res.json();
      setProjects(data);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Register new project
  const handleRegister = async () => {
    try {
      await fetch(`${API_URL}/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projectId, metadataCID }),
      });

      setProjectId("");
      setMetadataCID("");

      // Refresh list
      fetchProjects();
    } catch (err) {
      console.error("Failed to register project:", err);
    }
  };

  return (
    <View className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold">{t("admin_dashboard")}</Text>

      <TextInput
        className="border p-2 my-2"
        placeholder={t("project_id")}
        value={projectId}
        onChangeText={setProjectId}
      />

      <TextInput
        className="border p-2 my-2"
        placeholder={t("metadata_cid")}
        value={metadataCID}
        onChangeText={setMetadataCID}
      />

      <Button title={t("register_project")} onPress={handleRegister} color="#4CAF50" />

      <FlatList
        data={projects}
        renderItem={({ item }) => (
          <Text>{item.projectId}: {item.projectType ?? "N/A"}</Text>
        )}
        keyExtractor={(item, index) => item.projectId ?? index.toString()}
      />

      <LineChart
        data={{
          labels: ["Available", "Sold", "Retired"],
          datasets: [{ data: [39, 37, 33], color: () => "#4CAF50" }],
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
