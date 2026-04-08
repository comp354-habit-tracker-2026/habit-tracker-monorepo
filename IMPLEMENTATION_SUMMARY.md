# Disconnect Third-Party Apps Feature - Implementation Summary

## User Story
As a registered user, I want to manage my privacy by disconnecting linked third-party apps (like Strava) so that the system no longer accesses my external data.

### Acceptance Criteria
✅ User can view currently linked accounts on the settings screen  
✅ User can click disconnect and is prompted with a confirmation dialogue  
✅ System deletes the external access token upon confirmation  
✅ System stops data syncing with the disconnected provider  

---

## Backend Implementation (Django REST Framework)

### 1. New ViewSet: `ConnectedAccountViewSet`
**File:** `backend/activities/presentation/connected_account_viewset.py`

- Lists all connected accounts for the authenticated user
- Provides a `disconnect` action that:
  - Clears `access_token` and `refresh_token` from the database
  - Prevents future API calls to external providers
  - Optionally deletes associated activities
  - Returns success confirmation with provider name

### 2. New Serializer: `ConnectedAccountSerializer`
**File:** `backend/activities/serializers.py` (added)

- Serializes `ConnectedAccount` model without exposing tokens
- Shows provider name, external user ID, and connection date
- Read-only fields ensure tokens cannot be exposed

### 3. Updated URLs
**File:** `backend/activities/urls.py`

- Added route: `POST /api/v1/activities/connected-accounts/{id}/disconnect/`
- Integrated `ConnectedAccountViewSet` into router

### 4. Security Features
- Uses `IsAuthenticated` permission class
- Implements `IsAdminOrOwner` permission to prevent users from disconnecting other users' accounts
- User queryset filtering ensures only own accounts are visible
- Tokens are cleared instead of deleted to maintain activity history

---

## Frontend Implementation (React + TypeScript 5.9.3)

### 1. API Client Hook
**File:** `frontend/src/lib/connected-accounts-api.ts`

- `fetchConnectedAccounts()`: GET list of user's connected accounts
- `disconnectAccount(accountId, deleteActivities)`: POST disconnect request

### 2. Confirmation Dialog Component
**File:** `frontend/src/components/confirm-dialog.tsx`

- Reusable modal dialog for destructive actions
- Supports loading state during async operations
- Customizable titles, messages, and button text
- Supports "dangerous" (red) button styling
- Prevents background interaction when open

**Styling:** `frontend/src/components/confirm-dialog.css`

### 3. Connected Accounts Settings Component  
**File:** `frontend/src/components/connected-accounts-settings.tsx`

- Displays list of currently connected accounts with:
  - Provider name (e.g., "Strava")
  - External user ID
  - Connection date
  - Disconnect button
- Uses React Query for state management:
  - `useQuery` for fetching accounts
  - `useMutation` for disconnect operation
  - Auto-refetch after successful disconnect
- Shows loading and error states
- Integrates with ConfirmDialog for user confirmation

**Styling:** `frontend/src/components/connected-accounts-settings.css`

### 4. Updated Profile Route
**File:** `frontend/src/app/routes/app/profile.tsx`

- Integrated `ConnectedAccountsSettings` component
- Updated page title to "Profile & Settings"
- Added CSS module for layout

---

## Technical Decisions

### Token Clearing vs. Account Deletion
- **Decision:** Clear tokens instead of deleting the account
- **Reason:** Preserves activity history for analytics; user can reconnect without data loss

### Two-Step Confirmation
- **Confirmation Dialog:** Prevents accidental disconnection
- **API-side Validation:** Verifies user ownership of account

### React Query for State Management
- Automatic refetching after mutation
- Built-in loading/error states
- Prevents unnecessary API calls

### Responsive Design
- Works on desktop and mobile
- Dialog centers on screen
- List items adapt to screen size

---

## API Contract

### GET `/api/v1/activities/connected-accounts/`
**Response:**
```json
[
  {
    "id": 1,
    "provider": "strava",
    "provider_display": "Strava",
    "external_user_id": "12345",
    "connected_at": "2026-04-01T10:30:00Z"
  }
]
```

### POST `/api/v1/activities/connected-accounts/{id}/disconnect/`
**Request Body:**
```json
{
  "delete_activities": false
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully disconnected strava account.",
  "provider": "strava",
  "activities_deleted": false
}
```

---

## File Structure

```
Backend:
├── backend/activities/
│   ├── presentation/
│   │   ├── connected_account_viewset.py (NEW)
│   │   ├── __init__.py (UPDATED)
│   │   └── viewsets.py
│   ├── serializers.py (UPDATED - added ConnectedAccountSerializer)
│   ├── urls.py (UPDATED)
│   └── views.py (UPDATED)

Frontend:
├── frontend/src/
│   ├── lib/
│   │   └── connected-accounts-api.ts (NEW)
│   ├── components/
│   │   ├── confirm-dialog.tsx (NEW)
│   │   ├── confirm-dialog.css (NEW)
│   │   ├── connected-accounts-settings.tsx (NEW)
│   │   └── connected-accounts-settings.css (NEW)
│   └── app/routes/app/
│       ├── profile.tsx (UPDATED)
│       └── profile.css (NEW)
```

---

## Dependencies Used

### Backend
- Django 6.0.2 (existing)
- Django REST Framework 3.16.1 (existing)

### Frontend
- React 19.2.0 (existing)
- TypeScript 5.9.3 (existing)
- TanStack React Query 5.90.21 (existing)
- Axios 1.13.5 (existing)

**No new dependencies were added** - all code uses existing project dependencies.

---

## Testing the Feature

### Backend
1. Create a test user with a connected Strava account
2. GET `/api/v1/activities/connected-accounts/` - should list the account
3. POST `/api/v1/activities/connected-accounts/{id}/disconnect/` - should clear tokens
4. Verify `access_token` and `refresh_token` are NULL in database
5. Future data syncs will fail due to missing tokens

### Frontend
1. Navigate to `/app/profile`
2. See "Connected Third-Party Apps" section
3. View list of connected accounts
4. Click "Disconnect" button
5. Confirm in dialog
6. See account disappear from list

---

## Data Sync Prevention

Since the `access_token` is `NULL` after disconnection:
- Any API call to Strava using `account.access_token` will fail
- The `StravaActivityFetcher` will raise an error when trying to use None as Bearer token
- No further data syncing will occur
- User can reconnect to re-enable syncing

---

## Privacy & Security

✅ Tokens cleared from database  
✅ Prevents unauthorized access to external data  
✅ User ownership validated on backend  
✅ Sensitive tokens never exposed in API responses  
✅ Confirmation dialog prevents accidental loss of access  
