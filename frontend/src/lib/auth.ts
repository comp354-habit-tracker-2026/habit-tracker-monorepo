const ACCESS_TOKEN_KEY = 'habit-tracker-access-token';
const REFRESH_TOKEN_KEY = 'habit-tracker-refresh-token';

export const getAccessToken = () => {
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = () => {
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setAuthTokens = (accessToken: string, refreshToken: string) => {
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

export const clearAuthTokens = () => {
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const isAuthenticated = () => Boolean(getAccessToken());
