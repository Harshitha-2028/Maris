
  

const MONGODB_URI = 'mongodb+srv://harshitha040506_db_user:6uz3cjyHc2PSdUKz@bluecarbonregistry.ju9k4th.mongodb.net/bluecarbon?retryWrites=true&w=majority';

import { View, Text, FlatList } from "react-native";

import { LineChart } from "react-native-chart-kit";

import { useState, useEffect } from "react";

import { MongoClient } from "mongodb";

import { useTranslation } from "react-i18next";

  

export default function UserDashboard() {

const { t } = useTranslation();

const [credits, setCredits] = useState([]);

  

useEffect(() => {

const fetchCredits = async () => {

const client = new MongoClient(MONGODB_URI);

await client.connect();

const db = client.db("bluecarbon");

const data = await db.collection("credits").find().toArray();

setCredits(data);

};

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

keyExtractor={(item) => item.tokenId}

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