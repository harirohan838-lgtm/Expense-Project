import React,{useState} from "react";
import {ScrollView,View,Text,TextInput,Button,StyleSheet,Alert} from "react-native";
import {apiFetch} from "../api";
const cats=["Travel","Meals","Accommodation","Office Supplies","Client Entertainment","Other"];
export default function NewExpenseScreen({session,onDone}){
 const [f,setF]=useState({title:"",category:"Travel",amount:"",expense_date:new Date().toISOString().slice(0,10),description:"",receipt_filename:""});
 const u=(k,v)=>setF({...f,[k]:v});
 async function save(submit){try{const x=await apiFetch("/expenses",{method:"POST",body:JSON.stringify({...f,amount:Number(f.amount)})},session.token);if(submit)await apiFetch(`/expenses/${x.id}/submit`,{method:"POST"},session.token);Alert.alert("Success",submit?"Expense submitted.":"Draft saved.");onDone()}catch(e){Alert.alert("Error",e.message)}}
 return <ScrollView contentContainerStyle={s.container}><Text style={s.heading}>New Expense</Text>
 {["title","amount","expense_date","description","receipt_filename"].map(k=><View key={k}><Text style={s.label}>{k}</Text><TextInput style={s.input} value={f[k]} onChangeText={v=>u(k,v)} keyboardType={k==="amount"?"decimal-pad":"default"}/></View>)}
 <Text style={s.label}>Category</Text>{cats.map(c=><Button key={c} title={f.category===c?`✓ ${c}`:c} onPress={()=>u("category",c)}/>)}<View style={{height:12}}/><Button title="Save Draft" onPress={()=>save(false)}/><View style={{height:10}}/><Button title="Save & Submit" onPress={()=>save(true)}/>
 </ScrollView>
}
const s=StyleSheet.create({container:{padding:18},heading:{fontSize:24,fontWeight:"700",marginBottom:12},label:{fontWeight:"600",marginTop:10,marginBottom:5},input:{backgroundColor:"#fff",borderWidth:1,borderColor:"#ddd",padding:11,borderRadius:8}})
