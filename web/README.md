# Message Investigator - Frontend

AI Suspicious Message Investigation Agent frontend built with React 18, TypeScript, Vite, and Tailwind CSS.

## Features

- **Text-only analysis**: URLs are defanged and never opened
- **Mock mode**: Full functionality without backend for development/demo
- **Evidence highlighting**: Character-offset based highlighting of suspicious patterns
- **Risk assessment**: Multi-factor analysis with uncertainty indicators
- **Incident management**: Save and review investigations
- **Responsive design**: Works on desktop and mobile (390px+)

## Setup

### Install dependencies

```bash
npm install
```

### Development

Run with mock mode (default for development):

```bash
npm run dev
```

The app will be available at `http://localhost:5173`. API calls are proxied to `http://localhost:8000` in development when not using mocks.

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

- `VITE_USE_MOCKS=true` - Use mock data (no backend required)
- `VITE_USE_MOCKS=false` - Use real backend API at `/api/*`

### Build

```bash
npm run build
```

The build output goes to `dist/` and is served by FastAPI in production.

### Testing

```bash
npm run test
```

## Architecture

- **Routes**: `/` (investigate), `/results`, `/review`, `/incidents`, `/incidents/:id`
- **State**: Investigation context persisted to sessionStorage
- **API**: TanStack Query for data fetching with mock/real backend switching
- **Components**: Modular components following the design system

## Hard Rules

1. Text-only analysis - URLs never fetched/opened, shown defanged
2. Plain text rendering - No dangerouslySetInnerHTML, evidence highlighted via character offsets
3. No "safe" label - Lowest is "Low / Inconclusive"
4. Uncertainty banner always visible
5. Three indicator states: detected, not_detected, not_assessable
6. Nothing saved before explicit approval - incident ID only shown after API confirms
7. Errors preserve all user input with Retry option
8. No secrets in frontend - sessionStorage only for in-progress investigation

## Mock Mode

When `VITE_USE_MOCKS=true`, the mock server supports:
- Full High Risk assessment for password request messages
- Clarification response for messages under 20 characters
- Forced error when message contains `[force-error]`
- In-memory incidents list with auto-generated IDs (INC-0001...)
- Not-assessable indicator for IP address hosts

Mock data uses only fictitious domains (.test, .example) and 192.0.2.x addresses.
