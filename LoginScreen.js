import React,{useState} from "react";
import {View,Text,TextInput,Button,StyleSheet,Alert} from "react-native";
import {apiFetch} from "../api";
export default function LoginScreen({onLogin}){
 const [email,setEmail]=useState("amit@beeja.com");
 async function submit(){try{onLogin(await apiFetch("/auth/login",{method:"POST",body:JSON.stringify({email,role:"employee"})}))}catch(e){Alert.alert("Login failed",e.message)}}
 return <View style={s.container}><Text style={s.title}>Employee Login</Text><TextInput style={s.input} autoCapitalize="none" value={email} onChangeText={setEmail} placeholder="Email"/><Button title="Login" onPress={submit}/><Text style={s.hint}>amit@beeja.com · neha@beeja.com · rahul@beeja.com</Text></View>
}
const s=StyleSheet.create({container:{flex:1,justifyContent:"center",padding:24},title:{fontSize:28,fontWeight:"700",marginBottom:20},input:{backgroundColor:"#fff",borderWidth:1,borderColor:"#ddd",padding:12,borderRadius:8,marginBottom:12},hint:{marginTop:16,color:"#667085"}})
