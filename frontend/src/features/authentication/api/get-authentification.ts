//copy from Brandon Cameron get-activities.ts

//import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';

type userRegist = {
  'username': string;
  'email': string;
  'password': string;
  'password2': string;
}
type userLogin = {
  'username': string;
  'password': string;
}

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------
// async function checkRegistration(): Promise<User[]> {
//   const response = await apiClient.get<{ results: User[] }>('/api/v1/auth/register/');
//   return (response as unknown as { results: User[] }).results;
// }
// async function checkLogin(): Promise<User[]> {
//   const response = await apiClient.get<{ results: User[] }>('/api/v1/auth/login/');
//   return (response as unknown as { results: User[] }).results;
// }
async function checkRegistration(data: userRegist) {
  const response = await apiClient.post('/api/v1/auth/register/', data);
  return response;
}
async function checkLogin(data: userLogin) {
  const response = await apiClient.post('/api/v1/auth/login/', data);
  return response;
}

// ---------------------------------------------------------------------------
// Query options factory – keeps queryKey and fetcher colocated
// ---------------------------------------------------------------------------
// export function getRegistrationQueryOptions() {
//   return queryOptions({
//     queryKey: ['register'],
//     queryFn: getRegistration,
//   });
// }
// export function getLoginQueryOptions() {
//   return queryOptions({
//     queryKey: ['login'],
//     queryFn: getLogin,
//   });
// }

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useRegistration(data: userRegist) {
  return checkRegistration(data);
}
export function useLogin(data: userLogin) {
  return checkLogin(data);
}
