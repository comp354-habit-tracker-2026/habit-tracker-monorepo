//code from https://www.youtube.com/watch?v=X3qyxo_UTR4&t=763s
//https://github.com/gitdagray/react_login_form
//error help from ChatGPT
//err help from https://stackoverflow.com/questions/60151181/object-is-of-type-unknown-typescript-generics
import { Link } from 'react-router';
import { paths } from '@/config/paths';

//import React from "react";
import { useRef, useState, useEffect} from 'react';
//import { useRef, useState, useEffect, useContext } from 'react';
//import AuthContext from '../context/auth-provider';
// import { useLogin } from '../api/get-authentification';

export function Login () {
  //const { setAuth } = useContext(AuthContext);
  const userRef = useRef<HTMLInputElement | null>(null);
  const errRef = useRef<HTMLParagraphElement | null>(null);
  
  const [user, setUser] = useState<string>("");
  const [pwd, setPwd] = useState<string>("");
  const [errMsg, setErrMsg] = useState<string>("");
  const [success, setSuccess] = useState(false);

  useEffect(() => { userRef.current?.focus();
  }, [])
  
  //(e)
  //chat
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setUser('');
    setPwd('');
    setSuccess(true);
    //console.log(user, pwd);
    // try {
    //   const response = await axiosCreate.post(LOGIN_URL, 
    //     {user, pwd},
    //   const response = await apiClient.post(LOGIN_URL, 
    //     {user, pwd},
    //     //JSON.stringify({userName: user, passWord: pwd})) 
    //   {
    //     headers: { 'Content-Type': 'application/json'},
    //     withCredentials: true
    //   }
    //   );
    //   console.log(JSON.stringify(response?.data)); //chat
    //   //console.log(JSON.stringify(response));
    //   const accessToken = response?.data?.accessToken;
    //   const roles = response?.data?.roles; //chat
    //   setAuth({ user, pwd, roles, accessToken });      
    //   setUser('');
    //   setPwd('');
    //   setSuccess(true);
    // } catch (err) {
    //   if (err instanceof Error) {
    //     if (!err.response) {
    //       setErrMsg("No Server Response");
    //     } else if (err.response.status === 400) {
    //       setErrMsg("Missing Username or Password");
    //     } else if (err.response.status === 401) {
    //       setErrMsg("Unauthorized");
    //     } else {
    //       setErrMsg("Login Failed");
    //     }
    //     } else {
    //       setErrMsg("Unexpected Error");
    //     }

    //     errRef.current?.focus();
    // }
  }

  //error message
  return (
    <>
      {success ? (
        <div 
          style={{
            display: 'flex',
            height: '100vh',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            gap: '1rem',
          }}>
          <section>
            <h1>You are logged in!</h1>
            <br />
            <p>
              <Link to={paths.home.getHref()}>Go to Home</Link>
              <Link to={paths.app.root.getHref()}><br />To Dashboard</Link>
            </p>
          </section>
        </div>
      ) : (
    <div
       style={{
          alignItems: 'center',
        }}
      >
      <section> 
        <p ref = {errRef} 
        className = {errMsg ? "errmsg" : "offscreen"} 
        aria-live = "assertive"
        > 
          {errMsg}
        </p>
        <Link to={paths.home.getHref()}>Turn Back<br /><br /></Link>
        <form onSubmit = {handleSubmit}>
          <label htmlFor = 'username'>Username:<br /></label>
          <input
              type = "text"
              id = "username"
              ref = {userRef}
              autoComplete='off'
              onChange={(e) => {
                    setUser(e.target.value);
                    if (errMsg) setErrMsg("");
                  }}
              value = {user}
              required
              />
          <label htmlFor = 'passwword'><br />Passwword:<br /></label>
          <input
              type = "password"
              id = "passwword"
              onChange={(e) => {
                    setPwd(e.target.value);
                    if (errMsg) setErrMsg("");
                  }}
              value = {pwd}
              required
              /> <br /> <br />
          <button>Sign In</button>
        </form> 
        <p> <br />
          Need an Account?<br />
          <span className = "line">
            <a href = {paths.auth.register.getHref()}>Sign Up</a>
          </span>
        </p>
      </section>
      </div>  
        )}
      </>
  )
}