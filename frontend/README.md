# LuminaLib Frontend

Next.js frontend for LuminaLib library management system.

## Tech Stack

- Next.js 14.2.5 (App Router)
- React 18.2.0
- TypeScript 5.x
- Tailwind CSS 3.4.1
- @tabler/icons-react
- Jest + React Testing Library

## Setup

### Using Docker

See the main project [README.md](../README.md) for docker-compose instructions.

### Local Development

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment:**
   ```bash
   # Set API URL (optional, defaults to http://localhost:8000)
   export NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start Development Server:**
   ```bash
   npm run dev
   ```

Application will be available at `http://localhost:3000`

## Available Scripts

```bash
npm run dev      # Development server with hot reload
npm run build    # Production build
npm start        # Start production server
npm run lint     # Run ESLint
npm test         # Run tests
```

## Project Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - Reusable React components
- `src/lib/` - API client (`api.ts`) and utilities (`auth-context.tsx`)

All API calls go through `src/lib/api.ts`. Components never call `fetch` directly; they use `api.auth.*`, `api.books.*`, etc.

## Code Quality

```bash
npm run lint     # Check for linting errors
npm test         # Run tests
```
