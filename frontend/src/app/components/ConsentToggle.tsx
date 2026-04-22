import React from 'react';

interface ConsentToggleProps {
  provider: string;
  consentGranted: boolean;
  onToggle: (provider: string, consentGranted: boolean) => void;
}

export const ConsentToggle: React.FC<ConsentToggleProps> = ({ provider, consentGranted, onToggle }) => {
  return (
    <label style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer', userSelect: 'none' }}>
      <span>{provider}</span>
      <span style={{ display: 'inline-block', position: 'relative', width: 48, height: 28 }}>
        <input
          type="checkbox"
          checked={consentGranted}
          onChange={e => onToggle(provider, e.target.checked)}
          style={{
            opacity: 0,
            width: '100%',
            height: '100%',
            position: 'absolute',
            left: 0,
            top: 0,
            margin: 0,
            cursor: 'pointer',
            zIndex: 2,
          }}
        />
        <span
          style={{
            display: 'block',
            width: 48,
            height: 28,
            borderRadius: 28,
            background: consentGranted ? '#4f8cff' : '#111',
            transition: 'background 0.2s',
            position: 'absolute',
            left: 0,
            top: 0,
            boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
          }}
        />
        <span
          style={{
            display: 'block',
            width: 22,
            height: 22,
            borderRadius: '50%',
            background: '#fff',
            position: 'absolute',
            top: 3,
            left: consentGranted ? 24 : 3,
            transition: 'left 0.2s',
            boxShadow: '0 1px 4px rgba(0,0,0,0.18)',
          }}
        />
      </span>
    </label>
  );
};
