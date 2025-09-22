
  

import { useEffect } from "react";

import { View, Text, Image } from "react-native";

import { useRouter } from "expo-router";

import { speak } from "expo-speech";

import AsyncStorage from "@react-native-async-storage/async-storage";

  

export default function Splash() {

const router = useRouter();

useEffect(() => {

const checkOffline = async () => {

const offline = await AsyncStorage.getItem("offlineMode");

if (offline) {

alert("Offline Mode: Some features may be limited.");

}

speak("Welcome", { language: "en-IN" });

setTimeout(() => router.replace("/login"), 3000);

};

checkOffline();

}, []);

return (

<View className="flex-1 bg-primary justify-center items-center">

<Image source={require("@assets/tree.png")} className="w-24 h-24" />

<Text className="text-white text-2xl font-bold">Blue Carbon Registry</Text>

<Text className="text-white text-base">Empowering Coastal Conservation</Text>

</View>

);

}