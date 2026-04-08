import * as React from 'react';
import { createRoot } from 'react-dom/client';

import './index.css';
import { App } from '@/app/index';

const root = document.getElementById('root');
if (!root) throw new Error('Root element #root not found in index.html');

createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
