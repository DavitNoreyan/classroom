
import { $authHost, $host } from "./index";
import jwt_decode from "jwt-decode";

export const login = async (username, password) => {
  const {data} = await $host.post('/admin/login', {username, password})
  localStorage.setItem('token', data.token)
  return jwt_decode(data.token)
}

export const check = async () => {
  const {data} = await $authHost.get('/admin/admin_page')
  localStorage.setItem('token', data.token)
  return jwt_decode(data.token)
}