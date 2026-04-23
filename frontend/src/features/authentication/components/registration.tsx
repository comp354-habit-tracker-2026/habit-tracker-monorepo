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
import { checkRegistration } from '@/features/authentication/api/get-authentification';
import * as emailValidator from 'email-validator';

//chat
const USER_REGEX = /^[A-Za-z0-9_-]{3,23}$/;
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*(\d|[!@#$%])).{8,24}$/;
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
    const [userFocus, setUserFocus] = useState(false);
    const validName = USER_REGEX.test(user);

    const [email, setEmail] = useState('');
    const [emailFocus, setEmailFocus] = useState(false);
    const validEmail = emailValidator.validate(email);

    const [pwd, setPwd] = useState('');
    const [pwdFocus, setPwdFocus] = useState(false);

    const [matchPwd, setMatchPwd] = useState('');
    const [matchFocus, setMatchFocus] = useState(false);

    const validMatch = pwd === matchPwd;
    const validPwd = PWD_REGEX.test(pwd);

    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);
    
    useEffect(() => {
        userRef.current?.focus();
    }, [])

    //(e): chat + suggestion to submit
    const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();
        //if button enabled with JS hack
        const v1 = USER_REGEX.test(user);
        const v2 = PWD_REGEX.test(pwd);
        if (!v1 || !v2) {
            setErrMsg("Invalid Entry");
            return;
        }

        const person: user = { 'username': user, 'email': email, 'password': pwd, 'password2': matchPwd };
        const response = await checkRegistration(person);

        if (!response?.ok) {

            let message = "Username is already taken.";

            if (response.status === 400) {
                message = "Registration failed.";
            }

            setErrMsg(message);
            return;
        }

        // success path
        setSuccess(true);
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
                            < br/>
                            Username:
                            <FontAwesomeIcon icon={faCheck} className={validName ? 'valid' : 'hide'} />
                            <FontAwesomeIcon icon={faTimes} className={validName || !user? 'hide' : 'invalid'} />
                            < br/>
                        </label>
                        <input
                            type="text"
                            id="username"
                            ref={userRef}
                            autoComplete="off"
                            //chat+suggestion
                            onChange={(e) => {
                                setUser(e.target.value);
                                setErrMsg('');
                            }}
                            value={user}
                            required
                            aria-invalid={validName ? "false" : "true"}
                            aria-describedby="uidnote"
                            onFocus={() => setUserFocus(true)}
                            onBlur={() => setUserFocus(false)}
                        />
                        <p id="uidnote" className={userFocus && user && !validName ? "instructions" : "offscreen"} style={{fontSize: "14px"}}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            4 to 24 characters.<br />
                            Letters, numbers, underscores, hyphens allowed.
                        </p>

                        <label htmlFor='email'>
                            < br/>
                            Email:
                            <FontAwesomeIcon icon={faCheck} className={validEmail ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validEmail || !email ? "hide" : "invalid"} />
                            < br/>
                        </label>
                        <input
                            type="email"
                            id="email"
                            onChange={(e) => {
                                setEmail(e.target.value);
                                setErrMsg('');
                            }}
                            value={email}
                            required
                            aria-invalid={email ? (validEmail ? "false" : "true") : "false"}
                            aria-describedby="emailnote"
                            onFocus={() => setEmailFocus(true)}
                            onBlur={() => setEmailFocus(false)}
                        />
                        <p id="emailnote" className={emailFocus && email && !validEmail ? "instructions" : "offscreen"} style={{fontSize: "14px"}}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            The email entered is not valid or it does not exist.                           
                        </p>

                        <label htmlFor="password">
                            < br/>
                            Password:
                            <FontAwesomeIcon icon={faCheck} className={validPwd ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validPwd || !pwd ? "hide" : "invalid"} />
                            < br/>
                        </label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => {
                                setPwd(e.target.value);
                                setErrMsg('');
                            }}
                            value={pwd}
                            required
                            aria-invalid={pwd ? (validPwd ? "false" : "true") : "false"}
                            aria-describedby="pwdnote"
                            onFocus={() => setPwdFocus(true)}
                            onBlur={() => setPwdFocus(false)}
                        />
                        <p id="pwdnote" className={pwdFocus && pwd && !validPwd ? "instructions" : "offscreen"} style={{fontSize: "14px"}}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                            Must have 8 characters minimum.<br />
                            Must not be common nor numeric only, use at least: <br />
                            _1 uppercase letter, <br />
                            _1 lowercase letters, <br />
                            _1 number or 1 special character.
                            </p>


                        <label htmlFor="confirm_pwd">
                            < br/>
                            Confirm Password:
                            <FontAwesomeIcon icon={faCheck} className={validPwd ? "valid" : "hide"} />
                            <FontAwesomeIcon icon={faTimes} className={validPwd || !pwd ? "hide" : "invalid"} />
                            < br/>
                        </label>
                        <input
                            type="password"
                            id="confirm_pwd"
                            onChange={(e) => {
                                setMatchPwd(e.target.value);
                                setErrMsg('');
                            }}
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
                        <button disabled={!validName || !validPwd ? true : false}>Sign Up</button>
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