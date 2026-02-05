# LuminaLib Frontend

Next.js frontend for LuminaLib library management system.

## Setup

```bash
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` if backend is not on `http://localhost:8000`.

## Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm start` - Production server
- `npm run lint` - Run ESLint
- `npm test` - Run tests

## Project Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - Reusable React components
- `src/lib/` - API client and utilities

API client functions are in `src/lib/api.ts`. All API calls go through this abstraction layer.
