import React, { useEffect, useState } from "react";
import { View, Text, TextInput, Button, FlatList, TouchableOpacity, ScrollView } from "react-native";
import Constants from "expo-constants";

const API_URL = Constants.expoConfig?.extra?.API_URL ?? "http://10.0.2.2:8000";
const MINTER_TOKEN = "minter-token-456";

export default function MinterDashboard() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [proofCID, setProofCID] = useState("");
  const [message, setMessage] = useState("");

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/projects`);
      const data = await res.json();
      const approved = Array.isArray(data) ? data.filter((p) => p.status === "active") : [];
      setProjects(approved);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleIssue = async () => {
    if (!selectedProject) {
      setMessage("Select a project first");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/credits/issue`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${MINTER_TOKEN}`,
        },
        body: JSON.stringify({
          to_address: toAddress,
          project_id: selectedProject.project_id,
          amount: Number(amount),
          proof_cid: proofCID || "ipfs://demo-proof",
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(`✅ ${data.message}`);
        setToAddress("");
        setAmount("");
        setProofCID("");
        fetchProjects();
      } else {
        setMessage(`❌ Error: ${data.detail || "Failed to issue"}`);
      }
    } catch (err) {
      console.error("Issue failed:", err);
      setMessage("❌ Issue failed");
    }
  };

  return (
    <ScrollView className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold mb-4">Minter Dashboard</Text>

      <Text className="text-lg font-semibold mb-2">Approved Projects</Text>
      <FlatList
        data={projects}
        keyExtractor={(item) => item.project_id}
        renderItem={({ item }) => (
          <TouchableOpacity
            className={`border rounded-lg p-3 mb-2 ${selectedProject?.project_id === item.project_id ? "bg-green-100" : ""}`}
            onPress={() => setSelectedProject(item)}
          >
            <Text className="font-semibold">{item.name || item.project_id}</Text>
            <Text className="text-xs text-gray-600">{item.project_type} • {item.location}</Text>
            <Text>Issued: {item.balances?.total_issued ?? 0}</Text>
            <Text>Circulating: {item.balances?.circulating ?? 0}</Text>
          </TouchableOpacity>
        )}
      />

      {selectedProject && (
        <View className="mt-4 border rounded-lg p-3">
          <Text className="font-semibold mb-2">Issue Credits for {selectedProject.project_id}</Text>
          <TextInput className="border p-2 my-2 rounded" placeholder="User Wallet Address (0x...)" value={toAddress} onChangeText={setToAddress} />
          <TextInput className="border p-2 my-2 rounded" placeholder="Amount of credits" keyboardType="numeric" value={amount} onChangeText={setAmount} />
          <TextInput className="border p-2 my-2 rounded" placeholder="Proof CID (ipfs://...)" value={proofCID} onChangeText={setProofCID} />
          <Button title="Issue Credits" color="#4CAF50" onPress={handleIssue} />
        </View>
      )}

      {message ? <Text className="mt-4 text-sm">{message}</Text> : null}
    </ScrollView>
  );
}
