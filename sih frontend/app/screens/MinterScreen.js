  

import { View, Text, TextInput, Button, TouchableOpacity } from "react-native";
import { useState } from "react";
import Voice from "@react-native-community/voice";
import { useTranslation } from "react-i18next";

// 👇 Replace with your backend URL (e.g., http://10.0.2.2:5000 for Android emulator)
const API_URL = "http://<your-backend-ip>:5000";

export default function MinterDashboard() {
  const { t } = useTranslation();
  const [plotId, setPlotId] = useState("");
  const [projectType, setProjectType] = useState("");

  const startListening = async (field) => {
    await Voice.start("en-IN");
    Voice.onSpeechResults = (e) => {
      if (field === "plotId") setPlotId(e.value[0]);
      else if (field === "projectType") setProjectType(e.value[0]);
    };
  };

  const handleUpload = async () => {
    try {
      await fetch(`${API_URL}/uploads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plotId, projectType }),
      });

      setPlotId("");
      setProjectType("");
    } catch (err) {
      console.error("Failed to upload data:", err);
    }
  };

  return (
    <View className="flex-1 bg-white p-4">
      <Text className="text-primary text-2xl font-bold">{t("minter_dashboard")}</Text>

      <TextInput
        className="border p-2 my-2"
        placeholder={t("plot_id")}
        value={plotId}
        onChangeText={setPlotId}
      />
      <TouchableOpacity onPress={() => startListening("plotId")}>
        <Text className="text-primary">{t("voice_input")}</Text>
      </TouchableOpacity>

      <TextInput
        className="border p-2 my-2"
        placeholder={t("project_type")}
        value={projectType}
        onChangeText={setProjectType}
      />
      <TouchableOpacity onPress={() => startListening("projectType")}>
        <Text className="text-primary">{t("voice_input")}</Text>
      </TouchableOpacity>

      <Button title={t("upload_data")} onPress={handleUpload} color="#4CAF50" />
    </View>
  );
}
