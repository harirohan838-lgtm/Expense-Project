export const API_BASE="http://YOUR_LOCAL_IP:8000";
export async function apiFetch(path,options={},token=null){
  const res=await fetch(`${API_BASE}${path}`,{...options,headers:{"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{}) ,...(options.headers||{})}});
  const data=await res.json(); if(!res.ok)throw new Error(data.detail||"API error"); return data;
}
