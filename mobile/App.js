import React,{useState} from "react";
import {SafeAreaView,View,Text,Button,StyleSheet} from "react-native";
import LoginScreen from "./src/screens/LoginScreen";
import ExpenseListScreen from "./src/screens/ExpenseListScreen";
import NewExpenseScreen from "./src/screens/NewExpenseScreen";
import ExpenseDetailScreen from "./src/screens/ExpenseDetailScreen";

export default function App(){
  const [session,setSession]=useState(null),[screen,setScreen]=useState("list"),[id,setId]=useState(null);
  if(!session)return <LoginScreen onLogin={setSession}/>;
  return <SafeAreaView style={s.container}>
    <View style={s.header}><Text style={s.title}>Expense Reports</Text><Text>{session.user.name}</Text></View>
    {screen==="list"&&<ExpenseListScreen session={session} onNew={()=>setScreen("new")} onOpen={x=>{setId(x);setScreen("detail")}}/>}
    {screen==="new"&&<NewExpenseScreen session={session} onDone={()=>setScreen("list")}/>}
    {screen==="detail"&&<ExpenseDetailScreen session={session} expenseId={id} onBack={()=>setScreen("list")}/>}
    <View style={s.nav}><Button title="Expenses" onPress={()=>setScreen("list")}/><Button title="New" onPress={()=>setScreen("new")}/><Button title="Logout" onPress={()=>setSession(null)}/></View>
  </SafeAreaView>
}
const s=StyleSheet.create({container:{flex:1,backgroundColor:"#f6f7fb"},header:{padding:18,backgroundColor:"#fff",borderBottomWidth:1,borderBottomColor:"#ddd"},title:{fontSize:22,fontWeight:"700"},nav:{flexDirection:"row",justifyContent:"space-around",padding:12,backgroundColor:"#fff",borderTopWidth:1,borderTopColor:"#ddd"}})
