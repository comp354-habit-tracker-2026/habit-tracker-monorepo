import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// import { apiClient } from '@/lib/api-client'; // Real implementation

export interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
}

// Temporary Local Mock Data
let mockPreferences: NotificationPreferences = {
  email_enabled: true,
  push_enabled: false,
};

/**
 * Temporary mock API fetch function
 */
const fetchPreferencesMock = async (): Promise<NotificationPreferences> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ...mockPreferences });
    }, 600); // simulate network latency
  });
};

/**
 * Temporary mock API update function
 */
const updatePreferencesMock = async (
  newPrefs: NotificationPreferences
): Promise<NotificationPreferences> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockPreferences = { ...newPrefs };
      resolve({ ...mockPreferences });
    }, 600);
  });
};

/*
// REAL API IMPLEMENTATION (Uncomment when backend is ready)
const fetchPreferences = async (): Promise<NotificationPreferences> => {
  // Our apiClient interceptor unwraps the Axios response and returns the data directly
  return apiClient.get('/api/v1/notifications/preferences') as Promise<NotificationPreferences>;
};

const updatePreferences = async (newPrefs: NotificationPreferences): Promise<NotificationPreferences> => {
  return apiClient.put('/api/v1/notifications/preferences', newPrefs) as Promise<NotificationPreferences>;
};
*/

// React Query Hooks

export const useNotificationPreferences = () => {
  return useQuery({
    queryKey: ['notificationPreferences'],
    queryFn: fetchPreferencesMock, // TODO: Replace with fetchPreferences when backend is ready
  });
};

export const useUpdateNotificationPreferences = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updatePreferencesMock, // TODO: Replace with updatePreferences when backend is ready
    onSuccess: (updatedPrefs) => {
      // Optimistically update the cache
      queryClient.setQueryData(['notificationPreferences'], updatedPrefs);
    },
  });
};
