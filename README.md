# Group 5 - Generic Fitness API Adapter
## Overview
This service converts activity data from different fitness apps into one standard format, so the rest of the system can use it easily and it normalizes data, so all activities are in a common format.
## What this service does
- Call all integration groups (Groups 1–4) to get activity data from APIs.
- Handle API failures – retry or handle errors gracefully.
- Handle missing or incomplete data – ensure data is usable.
- Provide a consistent interface for the backend / Group 6 – so other parts of the system don’t need to worry about API differences.
## What this service does NOT do
- It does not provide a user interface
- It does not store data long-term (backend responsibility)
- It does not replace integration groups (Groups 1–4)
- It does not guarantee data correctness from APIs
