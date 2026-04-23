//code from https://www.youtube.com/watch?v=X3qyxo_UTR4&t=763s
//error help from ChatGPT
//npm install react-hook-form
//npm list react-hook-form
import { Link } from 'react-router';
import { paths } from '@/config/paths';

//import React from "react";
import { useRef, useState, useEffect} from 'react';
//import { useRef, useState, useEffect, useContext } from 'react';
//import AuthContext from '../context/auth-provider';
// import axiosCreate from '.api/axiosCreate';
// const LOGIN_URL = '/auth';

const Login = () => {
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
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setUser('');
    setPwd('');
    setSuccess(true);
    //console.log(user, pwd);
    // try {
    //   const response = await axiosCreate.post(LOGIN_URL, 
    //     {user, pwd},
    //     //JSON.stringify({userName: user, passWord: pwd})) 
    //   {
    //     headers: { 'Content-Type': 'application/json'},
    //     withCredentials: true
    //   }
    //   );
    //   console.log(JSON.stringify(response?.data));
    //   //console.log(JSON.stringify(response));
    //   const accessToken = response?.data?.accessToken;
    //   const roles = response?.data?.roles;
    //   setAuth({ user, pwd, roles, accessToken });      
    //   setUser('');
    //   setPwd('');
    //   setSuccess(true);
    // } catch (err) {
    //   if (axiosCreate.isAxiosError(err)) {
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
        <section>
          <h1>You are logged in!</h1>
          <br />
          <p>
            <Link to={paths.home.getHref()}>Go to Home</Link>
            <Link to={paths.app.root.getHref()}><br />To Dashboard</Link>
          </p>
        </section>
      ) : (
    <section> 
      <p ref = {errRef} 
      className = {errMsg ? "errmsg" : "offscreen"} 
      aria-live = "assertive"
      > 
        {errMsg}
      </p>
      <h1>Sign In</h1>
      <Link to={paths.home.getHref()}>Turn Back</Link>
      <Link to={paths.app.root.getHref()}><br />To Dashboard</Link>
      <form onSubmit = {handleSubmit}>
        <label htmlFor = 'username'>Username: </label>
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
        <label htmlFor = 'passwword'><br />Passwword: </label>
        <input
            type = "password"
            id = "passwword"
            onChange={(e) => {
                  setPwd(e.target.value);
                  if (errMsg) setErrMsg("");
                }}
            value = {pwd}
            required
            /> <br />
        <button>Sign In</button>
      </form> 
      <p>
        Need an Account?<br />
        <span className = "line">
          {/*put router link to register here*/}
          <a href = '#'>Sign Up</a>
        </span>
      </p>
    </section>
      )}
      </>
  )
}

export default Login