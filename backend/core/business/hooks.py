'''
Name: Shiyuan Zhang (40228185)
File: hooks.py
Issue: #82

Goal: 
Publish an event to the Eventhub when Activity data is preprocessed and ready for downstream tasks

'''

class LoggingHook:
    def log_details(self, status, changed_fields, activity):
        print(
            'Logging: \n'
            f"Provider: {activity.get('provider')}, "
            f"External_id: {activity.get('external_id')}, "
            f'Status: {status}'
        )
        if status == 'SKIP':
            print('Activity already exists and has no changes. Skip.')
        if status == 'NEW':
            print('New Activity saved.')
        if status == 'UPDATE' and changed_fields:
            print(f'Existing activity found, differences in fields {changed_fields}. Activity updated.')
