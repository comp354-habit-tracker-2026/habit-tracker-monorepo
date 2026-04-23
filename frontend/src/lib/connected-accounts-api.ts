import { apiClient } from '@/lib/api-client';

export interface ConnectedAccount {
  id: number;
  provider: string;
  provider_display: string;
  external_user_id: string;
  connected_at: string;
}

/**
 * Fetch all connected accounts for the current user
 */
export async function fetchConnectedAccounts(): Promise<ConnectedAccount[]> {
  return apiClient.get('/api/v1/activities/connected-accounts/');
}

/**
 * Disconnect a linked account
 * @param accountId - The ID of the connected account to disconnect
 * @param deleteActivities - Whether to delete associated activities (default: false)
 */
export async function disconnectAccount(
  accountId: number,
  deleteActivities: boolean = false,
) {
  return apiClient.post(
    `/api/v1/activities/connected-accounts/${accountId}/disconnect/`,
    { delete_activities: deleteActivities },
  );
}
