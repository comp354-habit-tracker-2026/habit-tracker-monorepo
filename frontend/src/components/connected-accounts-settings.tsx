import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import { ConfirmDialog } from '@/components/confirm-dialog';
import {
  fetchConnectedAccounts,
  disconnectAccount,
  type ConnectedAccount,
} from '@/lib/connected-accounts-api';
import './connected-accounts-settings.css';

/**
 * Component to display and manage user's connected accounts.
 * Allows viewing linked providers and disconnecting them.
 */
export function ConnectedAccountsSettings() {
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<ConnectedAccount | null>(null);

  // Fetch connected accounts
  const {
    data: accounts = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['connectedAccounts'],
    queryFn: fetchConnectedAccounts,
  });

  // Mutation for disconnecting
  const { mutate: disconnect, isPending: isDisconnecting } = useMutation({
    mutationFn: (accountId: number) => disconnectAccount(accountId, false),
    onSuccess: () => {
      setConfirmDialogOpen(false);
      setSelectedAccount(null);
      // Refetch to update the list
      refetch();
    },
    onError: (error: Error) => {
      console.error('Failed to disconnect account:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Failed to disconnect'}`);
    },
  });

  const handleDisconnectClick = (account: ConnectedAccount) => {
    setSelectedAccount(account);
    setConfirmDialogOpen(true);
  };

  const handleConfirmDisconnect = () => {
    if (selectedAccount) {
      disconnect(selectedAccount.id);
    }
  };

  const handleCancelDisconnect = () => {
    setConfirmDialogOpen(false);
    setSelectedAccount(null);
  };

  if (isLoading) {
    return (
      <div className="connected-accounts-settings">
        <div className="connected-accounts-settings__loading">
          Loading connected accounts...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="connected-accounts-settings">
        <div className="connected-accounts-settings__error">
          Error loading connected accounts: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    );
  }

  return (
    <div className="connected-accounts-settings">
      <h2 className="connected-accounts-settings__title">Connected Third-Party Apps</h2>

      {accounts.length === 0 ? (
        <p className="connected-accounts-settings__empty">
          No connected accounts. Link an app to get started!
        </p>
      ) : (
        <div className="connected-accounts-settings__list">
          {accounts.map((account: ConnectedAccount) => (
            <div key={account.id} className="connected-account-item">
              <div className="connected-account-item__info">
                <h3 className="connected-account-item__provider">
                  {account.provider_display}
                </h3>
                <p className="connected-account-item__user-id">
                  Account: {account.external_user_id}
                </p>
                <p className="connected-account-item__connected-at">
                  Connected: {new Date(account.connected_at).toLocaleDateString()}
                </p>
              </div>
              <button
                className="connected-account-item__disconnect-btn"
                onClick={() => handleDisconnectClick(account)}
                disabled={isDisconnecting}
              >
                Disconnect
              </button>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={confirmDialogOpen}
        title="Disconnect Account?"
        message={`Are you sure you want to disconnect your ${selectedAccount?.provider_display} account? The system will stop accessing your external data.`}
        confirmText="Disconnect"
        cancelText="Cancel"
        isDangerous={true}
        isLoading={isDisconnecting}
        onConfirm={handleConfirmDisconnect}
        onCancel={handleCancelDisconnect}
      />
    </div>
  );
}
