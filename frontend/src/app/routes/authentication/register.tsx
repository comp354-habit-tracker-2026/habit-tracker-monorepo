//copy
//https://www.youtube.com/watch?v=brcHK3P6ChQ&t=2056s
//https://github.com/gitdagray/react_register_form/blob/main/src/Register.js

import { Link } from 'react-router';
import { paths } from '@/config/paths';
// import {useRef, useState, useEffect } from 'react';
// import { faCheck, faTimes, faInfoCircle } from "@fortawesome/free-solid-svg-icons";
// import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { apiClient } from '@/lib/api-client';

/**
 * Account Registration Page
 */

function RegisterRoute() {
  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <h1>Register</h1>
      <p>Please enter a username and password.</p>
      <Link to={paths.app.root.getHref()}>Get started</Link>
      <Link to={paths.home.getHref()}>To Home</Link>
    </div>
  );
}

// react-router lazy() requires a default export
export default RegisterRoute;