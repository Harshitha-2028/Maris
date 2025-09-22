import { View, Text, TextInput, Button, Picker } from "react-native";
import { useState } from "react";
import { useRouter } from "expo-router";
import { getAuth, signInWithEmailAndPassword } from "@react-native-firebase/auth";
import Voice from "@react-native-community/voice";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useTranslation } from "react-i18next";

// 👇 Replace with your backend URL
const API_URL = "http://<your-backend-ip>:5000";

export default function Login() {
  const { t, i18n } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("User");
  const [language, setLanguage] = useState("en-IN");

  const router = useRouter();
  const auth = getAuth();

  const startListening = async (field) => {
    await Voice.start(language);
    Voice.onSpeechResults = (e) => {
      if (field === "email") setEmail(e.value[0]);
      else if (field === "password") setPassword(e.value[0]);
    };
  };

  const handleLogin = async () => {
    try {
      // ✅ Firebase auth
      await signInWithEmailAndPassword(auth, email, password);

      // ✅ Save user in backend DB (not directly from frontend)
      const res = await fetch(`${API_URL}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, role, language }),
      });

      if (!res.ok) throw new Error("Failed to save user");

      // ✅ Cache locally for app use
      await AsyncStorage.setItem("user", JSON.stringify({ email, role, language }));

      alert(t("login_success"));
      router.replace(`/${role.toLowerCase()}`);
    } catch (error) {
      console.error(error);
      alert(t("login_failed"));
    }
  };

  return (
    <View className="flex-1 bg-white p-4 justify-center">
      <Text className="text-primary text-2xl font-bold mb-4">{t("login")}</Text>

      <TextInput
        className="border p-2 my-2"
        placeholder={t("email")}
        value={email}
        onChangeText={setEmail}
      />
      <Button title={t("voice_email")} onPress={() => startListening("email")} color="#4CAF50" />

      <TextInput
        className="border p-2 my-2"
        placeholder={t("password")}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title={t("voice_password")} onPress={() => startListening("password")} color="#4CAF50" />

      <Picker selectedValue={role} onValueChange={(value) => setRole(value)} className="border p-2 my-2">
        <Picker.Item label="Admin" value="Admin" />
        <Picker.Item label="Minter" value="Minter" />
        <Picker.Item label="User" value="User" />
      </Picker>

      <Picker
        selectedValue={language}
        onValueChange={(value) => {
          setLanguage(value);
          i18n.changeLanguage(value);
        }}
        className="border p-2 my-2"
      >
        <Picker.Item label="English (India)" value="en-IN" />
        <Picker.Item label="Hindi" value="hi-IN" />
        <Picker.Item label="Bengali" value="bn-IN" />
      </Picker>

      <Button title={t("login_button")} onPress={handleLogin} color="#4CAF50" />
    </View>
  );
}
