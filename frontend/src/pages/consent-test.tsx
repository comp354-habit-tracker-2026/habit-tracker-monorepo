import { useState } from 'react';


const PROVIDERS = [
  'Strava',
  'MapMyRun',
  'We Ski',
  'MyWhoosh',
] as const;
type Provider = typeof PROVIDERS[number];

type UserActivities = { provider: string; activities: string[] };

// Dummy API classes for each provider
class StravaAPI {
  static getUserActivities() {
    return { provider: 'Strava', activities: ['Run', 'Bike', 'Swim'] };
  }
}
class MapMyRunAPI {
  static getUserActivities() {
    return { provider: 'MapMyRun', activities: ['Run', 'Walk'] };
  }
}
class WeSkiAPI {
  static getUserActivities() {
    return { provider: 'We Ski', activities: ['Ski', 'Snowboard'] };
  }
}
class MyWhooshAPI {
  static getUserActivities() {
    return { provider: 'MyWhoosh', activities: ['Cycling'] };
  }
}

const PROVIDER_APIS = {
  Strava: StravaAPI,
  MapMyRun: MapMyRunAPI,
  'We Ski': WeSkiAPI,
  MyWhoosh: MyWhooshAPI,
};


export default function ConsentTest() {
  const [consents, setConsents] = useState<Record<Provider, boolean>>({} as Record<Provider, boolean>);
  const [userData, setUserData] = useState<Record<Provider, UserActivities>>({} as Record<Provider, UserActivities>);
  const [message, setMessage] = useState<string | null>(null);

  const handleToggle = (provider: Provider) => {
    setConsents((prev) => {
      const newState = { ...prev, [provider]: !prev[provider] };
      // If toggling ON, fetch dummy data from API
      if (!prev[provider]) {
        const api = PROVIDER_APIS[provider];
        if (api) {
          setUserData((data) => ({
            ...data,
            [provider]: api.getUserActivities(),
          }));
        }
        setMessage(null);
      } else {
        // If toggling OFF, remove user data and show confirmation
        setUserData((data) => {
          const newData = { ...data };
          delete newData[provider];
          return newData;
        });
        setMessage(`User data for ${provider} deleted after consent was revoked.`);
      }
      return newState;
    });
  };

  return (
    <div style={{ color: '#fff', padding: '2rem' }}>
      <h1 style={{ fontWeight: 700, fontSize: '2.5rem' }}>Consent Test</h1>
      <p style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
        This page is a small dummy test for the new consent API.
      </p>
      {PROVIDERS.map((provider) => (
        <div key={provider} style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem' }}>
          <span id={`provider-label-${provider.replace(/\s+/g, '-').toLowerCase()}`} style={{ fontSize: '1.5rem', minWidth: 120 }}>{provider}</span>
          <label className="switch">
            <input
              type="checkbox"
              aria-labelledby={`provider-label-${provider.replace(/\s+/g, '-').toLowerCase()}`}
              checked={!!consents[provider]}
              onChange={() => handleToggle(provider)}
            />
            <span className="slider round"></span>
          </label>
        </div>
      ))}
      <p style={{ fontSize: '1.25rem', marginTop: '2rem' }}>
        Toggle a provider to simulate a consent request.
      </p>
      <div style={{ marginTop: '2rem' }}>
        <h2 style={{ fontWeight: 700, fontSize: '1.5rem' }}>User Data (dummy):</h2>
        <pre>{JSON.stringify(userData, null, 2)}</pre>
        {message && (
          <div style={{ color: '#ffb347', marginTop: '1rem', fontWeight: 500 }}>
            {message}
          </div>
        )}
      </div>
      <style>{`
        .switch {
          position: relative;
          display: inline-block;
          width: 60px;
          height: 34px;
          margin-left: 1rem;
        }
        .switch input {display:none;}
        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #222;
          -webkit-transition: .4s;
          transition: .4s;
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 26px;
          width: 26px;
          left: 4px;
          bottom: 4px;
          background-color: white;
          -webkit-transition: .4s;
          transition: .4s;
        }
        input:checked + .slider {
          background-color: #2196F3;
        }
        input:focus + .slider {
          box-shadow: 0 0 1px #2196F3;
        }
        input:checked + .slider:before {
          -webkit-transform: translateX(26px);
          -ms-transform: translateX(26px);
          transform: translateX(26px);
        }
        .slider.round {
          border-radius: 34px;
        }
        .slider.round:before {
          border-radius: 50%;
        }
      `}</style>
    </div>
  );
}
