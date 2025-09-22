import React, { useEffect, useState } from "react";
import { View, Text, FlatList, TextInput, Button, ScrollView, TouchableOpacity } from "react-native";
import { LineChart } from "react-native-chart-kit";

// 👇 Replace with your backend URL
const API_URL = "http://<your-backend-ip>:8000";

// admin auth token (demo only, store securely in prod)
const ADMIN_TOKEN = "admin-token-123";

export default function AdminDashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [overview, setOverview] = useState<any | null>(null);
  const [history, setHistory] = useState<Record<string, any[]>>({});
  const [projectId, setProjectId] = useState("");
  const [metadataCID, setMetadataCID] = useState("");
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  // fetch registry overview
  const fetchOverview = async () => {
    try {
      const res = await fetch(`${API_URL}/`);
      const data = await res.json();
      setOverview(data);
    } catch (err) {
      console.error("Failed to fetch overview:", err);
    }
  };

  // fetch projects
  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/projects`);
      const data = await res.json();
      setProjects(data);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  // fetch history for a project
  const fetchHistory = async (pid: string) => {
    try {
      const res = await fetch(`${API_URL}/projects/${pid}/history`);
      const data = await res.json();
      setHistory((prev) => ({ ...prev, [pid]: data }));
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  useEffect(() => {
    fetchOverview();
    fetchProjects();
  }, []);

  // register new project
  const handleRegister = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/projects/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${ADMIN_TOKEN}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          metadata_cid: metadataCID,
          name: `Project ${projectId}`,
          description: "Demo project from admin UI",
          project_type: "Mangrove",
          location: "South India",
        }),
      });
      setProjectId("");
      setMetadataCID("");
      fetchProjects();
    } catch (err) {
      console.error("Failed to register project:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-white p-4">
      <Text className="text-xl font-bold mb-2">🌿 BlueCarbon Admin Dashboard</Text>

      {/* Overview KPIs */}
      {overview && (
        <View className="mb-4">
          <Text>Total Projects: {overview.projects}</Text>
          <Text>Total Credits Issued: {overview.total_credits_issued}</Text>
          <Text>Network: {overview.network}</Text>
        </View>
      )}

      {/* Register new project */}
      <View className="border rounded-lg p-3 mb-4">
        <Text className="text-lg font-semibold mb-2">Register New Project</Text>
        <TextInput
          className="border p-2 my-2 rounded"
          placeholder="Project ID"
          value={projectId}
          onChangeText={setProjectId}
        />
        <TextInput
          className="border p-2 my-2 rounded"
          placeholder="Metadata CID"
          value={metadataCID}
          onChangeText={setMetadataCID}
        />
        <Button title={loading ? "Registering..." : "Register Project"} onPress={handleRegister} />
      </View>

      {/* Projects list */}
      <View className="mb-6">
        <Text className="text-lg font-semibold mb-2">Projects</Text>
        <FlatList
          data={projects}
          keyExtractor={(item) => item.project_id}
          renderItem={({ item }) => {
            const isOpen = expanded === item.project_id;
            return (
              <View className="border rounded-lg p-3 mb-3">
                <TouchableOpacity
                  onPress={() => {
                    setExpanded(isOpen ? null : item.project_id);
                    if (!history[item.project_id]) fetchHistory(item.project_id);
                  }}
                >
                  <Text className="font-semibold">{item.name || item.project_id}</Text>
                  <Text className="text-xs text-gray-600">{item.project_type} • {item.location}</Text>
                  <Text className="mt-1">Credits Issued: {item.balances?.total_issued ?? 0}</Text>
                  <Text>Credits Retired: {item.balances?.total_retired ?? 0}</Text>
                  <Text>Circulating: {item.balances?.circulating ?? 0}</Text>
                </TouchableOpacity>

                {isOpen && (
                  <View className="mt-2">
                    <Text className="font-medium">History</Text>
                    {history[item.project_id] ? (
                      history[item.project_id].map((h, i) => (
                        <View key={i} className="border rounded p-2 mb-1">
                          <Text>{h.action}</Text>
                          <Text className="text-xs">{h.tx_hash}</Text>
                          <Text className="text-xs text-gray-600">
                            {new Date(h.timestamp).toLocaleString()}
                          </Text>
                        </View>
                      ))
                    ) : (
                      <Text className="text-xs text-gray-500">Loading...</Text>
                    )}
                  </View>
                )}
              </View>
            );
          }}
        />
      </View>

      {/* Transactions chart (placeholder using balances) */}
      <View className="border rounded-lg p-3 mb-10">
        <Text className="text-lg font-semibold mb-2">Credits Chart (Issued vs Retired)</Text>
        <LineChart
          data={{
            labels: projects.map((p) => p.project_id),
            datasets: [
              { data: projects.map((p) => p.balances?.total_issued ?? 0), color: () => "#4CAF50" },
              { data: projects.map((p) => p.balances?.total_retired ?? 0), color: () => "#F44336" },
            ],
          }}
          width={320}
          height={200}
          chartConfig={{
            backgroundColor: "#ffffff",
            backgroundGradientFrom: "#ffffff",
            backgroundGradientTo: "#ffffff",
            color: () => "#000",
            labelColor: () => "#000",
            decimalPlaces: 0,
          }}
        />
      </View>
    </ScrollView>
  );
}
