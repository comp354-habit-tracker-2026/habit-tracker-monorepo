//copy from Brandon Cameron activities-list
//copy
//https://www.youtube.com/watch?v=brcHK3P6ChQ&t=2056s
//https://github.com/gitdagray/react_register_form/blob/main/src/Register.js
//email validator
//https://stackoverflow.com/questions/72092658/how-can-i-validate-react-input-is-not-empty-and-valid-email
//https://github.com/manishsaraan/email-validator

import { Link } from 'react-router';
import { paths } from '@/config/paths';
import {useRef, useState, useEffect } from 'react';
import { faCheck, faTimes, faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useRegistration } from '@/features/authentication/api/get-authentification';
import * as emailValidator from 'email-validator';

const USER_REGEX = /^[A-z][A-z0-9-_]{3,23}$/; //recheck
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/; //recheck, min 8 length + 1 character
type user = {
  'username': string;
  'email': string;
  'password': string;
  'password2': string;
}

export function Registration() {
    const userRef = useRef<HTMLInputElement | null>(null);
    const errRef = useRef<HTMLInputElement | null>(null);

    const [user, setUser] = useState('');
    // const [validName, setValidName] = useState(false);
    const [validName] = useState(false);
    const [userFocus, setUserFocus] = useState(false);

    const [email, setEmail] = useState('');
    const [emailFocus, setEmailFocus] = useState(false);
    const validEmail = emailValidator.validate(email);

    const [pwd, setPwd] = useState('');
    // const [validPwd, setValidPwd] = useState(false);
    const [validPwd] = useState(false);
    const [pwdFocus, setPwdFocus] = useState(false);

    const [matchPwd, setMatchPwd] = useState('');
    // const [validMatch, setValidMatch] = useState(false);
    const [validMatch] = useState(false);
    const [matchFocus, setMatchFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);
    useEffect(() => {
        userRef.current?.focus();
    }, [])

    useEffect(() => {
        const result = USER_REGEX.test(user);
        console.log("user regex = ", result);
        console.log("user = ", user);
        //setValidName(USER_REGEX.test(user));
        //setValidName(user);
    }, [user])

    useEffect(() => {
        const resultPwd = PWD_REGEX.test(pwd);
        console.log("pwd regex = ", resultPwd);
        console.log("pwd = ", pwd);
        console.log("matchpwd = ", matchPwd);
        // setValidPwd(PWD_REGEX.test(pwd));
        // setValidMatch(pwd === matchPwd);
    }, [pwd, matchPwd])

    // useEffect(() => {
    //     setErrMsg('');
    // }, [user, pwd, matchPwd])

    const person: user = { 'username': user, 'email': '456', 'password': pwd, 'password2': matchPwd };
    const response = useRegistration(person);
    //(e): chat + suggestion to submit
    const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        // if button enabled with JS hack
        const v1 = USER_REGEX.test(user);
        const v2 = PWD_REGEX.test(pwd);
        if (!v1 || !v2) {
            setErrMsg("Invalid Entry");
            return;
        }

        if ((await response).status === 201){
            setSuccess(true); //check
        }
        else if ((await response).status === 400) {
            //username taken, password too short: >= 8 characters & too common & entirely numeric 
            setErrMsg((await response).statusText);
        }
        else if ((await response).status === 409) {
            setErrMsg("Username already taken.");
        }
        else {
            setErrMsg('Registration Failed.')
        }
        //errRef.current.focus();
    }

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
                        <h1>You are registered!</h1>
                        <br />
                        <p>
                        <Link to={paths.home.getHref()}>Return</Link>
                        <Link to={paths.auth.login.getHref()}><br />Sign In</Link>
                        </p>
                    </section>
                </div>
            ) : (
                <section>
                    <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">
                            Username:
                            <span className= {validName ? "valid" : "hide"}>
                                <FontAwesomeIcon icon={faCheck} className={validName ? "valid" : "hide"} />
                            </span>
                            <span className = {validName || !user ? "hide" : "invalid"}>
                                <FontAwesomeIcon icon={faTimes} className={validName || !user ? "hide" : "invalid"} />
                            </span>
                            
                        </label>
                        <input
                            type="text"
                            id="username"
                            ref={userRef}
                            autoComplete="off"
                            onChange={(e) => setUser(e.target.value)}
                            value={user}
                            required
                            aria-invalid={validName ? "false" : "true"}
                            aria-describedby="uidnote"
                            onFocus={() => setUserFocus(true)}
                            onBlur={() => setUserFocus(false)}
                        />
                        <p id="uidnote" className={userFocus && user && !validName ? "instructions" : "offscreen"}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            4 to 24 characters.<br />
                            Must begin with a letter.<br />
                            Letters, numbers, underscores, hyphens allowed.
                        </p>

                        <label htmlFor='email'>
                            Email:
                            <FontAwesomeIcon icon={faCheck} className={validEmail ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validEmail || !email ? "hide" : "invalid"} />
                        </label>
                        <input
                            type="email"
                            id="email"
                            onChange={(e) => setEmail(e.target.value)}
                            value={email}
                            required
                            aria-invalid={validEmail ? "false" : "true"}
                            aria-describedby="emailnote"
                            onFocus={() => setEmailFocus(true)}
                            onBlur={() => setEmailFocus(false)}
                        />
                        <p id="emailnote" className={emailFocus && !validEmail ? "instructions" : "offscreen"}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            The email entered is not valid or does not exist.< br/>                            
                        </p>

                        <label htmlFor="password">
                            Password:
                            <FontAwesomeIcon icon={faCheck} className={validPwd ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validPwd || !pwd ? "hide" : "invalid"} />
                        </label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => setPwd(e.target.value)}
                            value={pwd}
                            required
                            aria-invalid={validPwd ? "false" : "true"}
                            aria-describedby="pwdnote"
                            onFocus={() => setPwdFocus(true)}
                            onBlur={() => setPwdFocus(false)}
                        />
                        <p id="pwdnote" className={pwdFocus && !validPwd ? "instructions" : "offscreen"}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            8 to 24 characters.<br />
                            Must include uppercase and lowercase letters, a number and a special character.<br />
                            Allowed special characters: <span aria-label="exclamation mark">!</span> <span aria-label="at symbol">@</span> <span aria-label="hashtag">#</span> <span aria-label="dollar sign">$</span> <span aria-label="percent">%</span>
                        </p>


                        <label htmlFor="confirm_pwd">
                            Confirm Password:
                            <FontAwesomeIcon icon={faCheck} className={validMatch && matchPwd ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validMatch || !matchPwd ? "hide" : "invalid"} />
                        </label>
                        <input
                            type="password"
                            id="confirm_pwd"
                            onChange={(e) => setMatchPwd(e.target.value)}
                            value={matchPwd}
                            required
                            aria-invalid={validMatch ? "false" : "true"}
                            aria-describedby="confirmnote"
                            onFocus={() => setMatchFocus(true)}
                            onBlur={() => setMatchFocus(false)}
                        />
                        <p id="confirmnote" className={matchFocus && !validMatch ? "instructions" : "offscreen"}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            Must match the first password input field.
                        </p>
                        <br />
                        <button disabled={!validName || !validPwd || !validMatch ? true : false}>Sign Up</button>
                    </form>
                    <p>
                        Already registered?<br />
                        <span className="line">
                            <a href= {paths.auth.login.getHref()}>Sign In</a>
                        </span>
                    </p>
                </section>
            )}
        </>
    )
}