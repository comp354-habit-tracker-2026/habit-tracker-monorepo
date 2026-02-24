# Habit Tracker Monorepo

A simple habit tracker API with goal and template endpoints.

## Features

- **GET /goals/:id** - Retrieve a specific goal by ID
- **GET /goals/templates** - Retrieve all available goal templates

## Response Fields

Both endpoints return resources with the following fields:
- `id` - Unique identifier
- `userId` - User ID (for goals)
- `duration` - Duration in minutes
- `sport` - Sport/activity type
- `progressionType` - Type of progression (linear, exponential, step, custom)
- `reward` - Reward identifier

## Installation

```bash
npm install
```

## Running the API

```bash
# Development
npm run dev

# Production
npm start
```

## Testing

```bash
# Run tests
npm test

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

## API Endpoints

### Get Goal by ID

```
GET /goals/:id
```

**Example Response:**
```json
{
  "id": "goal-1",
  "userId": "user-1",
  "duration": 30,
  "sport": "running",
  "progressionType": "linear",
  "reward": "badge-marathon"
}
```

**Error Responses:**
- `400` - Invalid ID format
- `404` - Goal not found

### Get Goal Templates

```
GET /goals/templates
```

**Example Response:**
```json
{
  "count": 4,
  "templates": [
    {
      "id": "template-1",
      "duration": 30,
      "sport": "running",
      "progressionType": "linear",
      "reward": "badge-marathon"
    }
  ]
}
```
