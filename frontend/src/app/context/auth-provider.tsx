// import { createContext, useState } from 'react';

// const AuthContext = createContext({});

// export const AuthProvider = ({ children }) => {
//     const [auth, setAuth] = useState({});

//     return (
//         <AuthContext.Provider value = {{ auth, setAuth}}>
//             {children}
//         </AuthContext.Provider>
//     )
// }
//copy
// export default AuthContext;

import { createContext, useState, ReactNode } from 'react';

type AuthType = {
  user?: string;
  pwd?: string;
  roles?: string[];
  accessToken?: string;
};

type AuthContextType = {
  auth: AuthType;
  setAuth: React.Dispatch<React.SetStateAction<AuthType>>;
};

const AuthContext = createContext<AuthContextType | null>(null);

type Props = {
  children: ReactNode;
};

export const AuthProvider = ({ children }: Props) => {
  const [auth, setAuth] = useState<AuthType>({});

  return (
    <AuthContext.Provider value={{ auth, setAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;