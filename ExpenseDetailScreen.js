import React,{useEffect,useState} from "react";
import {View,Text,Button,StyleSheet,Alert} from "react-native";
import {apiFetch} from "../api";
export default function ExpenseDetailScreen({session,expenseId,onBack}){
 const [e,setE]=useState(null);
 async function load(){try{setE(await apiFetch(`/expenses/${expenseId}`,{},session.token))}catch(x){Alert.alert("Error",x.message)}}
 useEffect(()=>{load()},[expenseId]);
 if(!e)return <View style={s.container}><Text>Loading...</Text></View>;
 async function submit(){try{await apiFetch(`/expenses/${e.id}/submit`,{method:"POST"},session.token);load()}catch(x){Alert.alert("Error",x.message)}}
 return <View style={s.container}><Button title="Back" onPress={onBack}/><Text style={s.heading}>{e.title}</Text><Text>Category: {e.category}</Text><Text>Amount: ₹{Number(e.amount).toFixed(2)}</Text><Text>Date: {e.expense_date}</Text><Text>Status: {e.status}</Text><Text>Description: {e.description||"-"}</Text><Text>Receipt: {e.receipt_filename||"-"}</Text>{["draft","rejected"].includes(e.status)&&<View style={{marginTop:20}}><Button title="Submit Expense" onPress={submit}/></View>}</View>
}
const s=StyleSheet.create({container:{padding:20},heading:{fontSize:25,fontWeight:"700",marginVertical:15}})
