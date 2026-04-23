//code from https://www.youtube.com/watch?v=X3qyxo_UTR4&t=763s
//https://github.com/gitdagray/react_login_form
//error help from ChatGPT
//err help from https://stackoverflow.com/questions/60151181/object-is-of-type-unknown-typescript-generics
import { Link } from 'react-router';
import { paths } from '@/config/paths';

import React from "react";
import { useRef, useState, useEffect, useContext } from 'react';
import AuthContext from '@/app/context/auth-provider';
import { checkLogin } from '../api/get-authentification';
import axios from "axios";

type user = {
  'username': string;
  'password': string;
}

export function Login () {
  const authContext = useContext(AuthContext);
  if (!authContext) {
    throw new Error("AuthContext missing");
  }
  const { setAuth } = authContext;
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

    try {
      const person: user = { 'username': user, 'password': pwd };
      const response = await checkLogin(person);
      console.log(JSON.stringify(response?.data)); //chat
      const accessToken = response?.data?.accessToken;
      const roles = response?.data?.roles; //chat
      setAuth({ user, roles, accessToken });      
      setUser('');
      setPwd('');
      setSuccess(true);
    } catch (err) {
        if (axios.isAxiosError(err)) {
            const status = err.response?.status;

            const data = err.response?.data;

            console.log("backend error:", data);

            if (status === 400) {
                setErrMsg(
                    typeof data === "string"
                        ? data
                        : data?.detail ||
                        data?.message ||
                        JSON.stringify(data)
                );
            }
            else if (status === 401) {
              setErrMsg("Unauthorized");
            }
            else {
                setErrMsg("Login Failed");
            }

            errRef.current?.focus();
        } 
        else {
            setErrMsg("Unexpected Error");
        }
    
      }
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
        <h1>Sign In</h1>
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