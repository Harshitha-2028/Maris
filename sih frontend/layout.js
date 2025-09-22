
import { NativeWindStyleSheet } from "nativewind";

import { Stack } from "expo-router";

import { StatusBar } from "expo-status-bar";

  

NativeWindStyleSheet.setOutput({

default: "native",

});

  

export default function RootLayout() {

return (

<>

<StatusBar style="auto" />

<Stack>

<Stack.Screen name="index" options={{ headerShown: false }} />

<Stack.Screen name="login" options={{ headerShown: false }} />

<Stack.Screen name="admin" options={{ title: "Admin Dashboard" }} />

<Stack.Screen name="minter" options={{ title: "Minter Dashboard" }} />

<Stack.Screen name="user" options={{ title: "User Dashboard" }} />

</Stack>

</>

);

}