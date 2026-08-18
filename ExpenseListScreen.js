import React,{useEffect,useState} from "react";
import {View,Text,FlatList,Button,StyleSheet,RefreshControl} from "react-native";
import {apiFetch} from "../api";
export default function ExpenseListScreen({session,onNew,onOpen}){
 const [items,setItems]=useState([]),[refreshing,setRefreshing]=useState(false);
 async function load(){setRefreshing(true);try{setItems(await apiFetch(`/expenses?employee_id=${session.user.id}`,{},session.token))}finally{setRefreshing(false)}}
 useEffect(()=>{load()},[]);
 return <View style={s.container}><View style={s.row}><Text style={s.heading}>My Expenses</Text><Button title="New" onPress={onNew}/></View>
 <FlatList data={items} keyExtractor={x=>String(x.id)} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load}/>} ListEmptyComponent={<Text style={s.empty}>No expenses yet.</Text>}
 renderItem={({item})=><View style={s.card}><Text style={s.title}>{item.title}</Text><Text>₹{Number(item.amount).toFixed(2)} · {item.category}</Text><Text style={s.status}>{item.status}</Text><Button title="View" onPress={()=>onOpen(item.id)}/></View>}/></View>
}
const s=StyleSheet.create({container:{flex:1,padding:16},row:{flexDirection:"row",justifyContent:"space-between",alignItems:"center"},heading:{fontSize:22,fontWeight:"700"},card:{backgroundColor:"#fff",padding:16,borderRadius:12,marginTop:12},title:{fontSize:18,fontWeight:"700"},status:{marginVertical:7,fontWeight:"700"},empty:{textAlign:"center",marginTop:50,color:"#667085"}})
