//copy from Brandon Cameron get-activities.ts

//import { queryOptions, useQuery } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import axios from 'axios';

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
// export async function checkRegistration(data: userRegist) {
//   console.log("userRegist = ", data);
//   try {
//     const response = await apiClient.post('/api/v1/auth/register/', data)
//     if(!(response instanceof Error))
//     {
//       console.log("send post success");
//     }
//     return (response);
//   } catch(err) {
//     if(err instanceof Error)
//     {
//       console.log("error send post.");
//     }
//   };
// }
export async function checkRegistration(data: userRegist) {
  try {
    const response = await apiClient.post('/api/v1/auth/register/', data);

    return {
      ok: true,
      status: response.status,
      data: response.data,
      message: null,
    };
  } catch (err: unknown) {
      console.log("WRAPPER ERROR:", err);

      if (axios.isAxiosError(err)) {
          return {
              ok: false,
              status: err.response?.status ?? null,
              data: err.response?.data ?? null,
              message: err.message,
          };
      }

      return {
          ok: false,
          status: null,
          data: null,
          message: err instanceof Error ? err.message : "Unknown error",
      };
  }
}

export async function checkLogin(data: userLogin) {
  return await apiClient.post('/api/v1/auth/login/', data);
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
