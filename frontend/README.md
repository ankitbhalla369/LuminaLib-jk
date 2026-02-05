# LuminaLib Frontend

Modern, responsive React/Next.js frontend for the LuminaLib library management system with a clean UI and comprehensive testing.

## Tech Stack

- **Framework:** [Next.js](https://nextjs.org/) 14.2.5 (React framework with App Router)
- **React:** 18.2.0 (UI library)
- **Language:** [TypeScript](https://www.typescriptlang.org/) 5.x (Type-safe JavaScript)
- **Styling:**
  - [Tailwind CSS](https://tailwindcss.com/) 3.4.1 (Utility-first CSS framework)
  - Custom CSS modules for component-specific styles
- **Icons:** [@tabler/icons-react](https://tabler-icons.io/) 3.23.0 (Beautiful icon library)
- **Notifications:** [react-hot-toast](https://react-hot-toast.com/) 2.6.0 (Toast notifications)
- **HTTP Client:** Native fetch API (built into Next.js)
- **Testing:**
  - [Jest](https://jestjs.io/) 29.7.0 (Test framework)
  - [React Testing Library](https://testing-library.com/react) 14.2.1 (Component testing)
  - [@testing-library/jest-dom](https://github.com/testing-library/jest-dom) 6.4.2 (Custom matchers)
- **Build Tools:**
  - [PostCSS](https://postcss.org/) (CSS processing)
  - [Autoprefixer](https://github.com/postcss/autoprefixer) (CSS vendor prefixes)
  - [SWC](https://swc.rs/) (Fast TypeScript/JavaScript compiler)
- **Code Quality:**
  - [ESLint](https://eslint.org/) 8.x (Linting)
  - [eslint-config-next](https://nextjs.org/docs/app/building-your-application/configuring/eslint) (Next.js ESLint rules)

## Features Implemented

### 1. Authentication System
- **User Registration:** Sign-up form with validation
- **User Login:** JWT-based authentication
- **Auth Context:** React Context API for global auth state management
- **Protected Routes:** Automatic redirect to login for unauthenticated users
- **Persistent Sessions:** Token stored in localStorage with auto-login
- **Logout:** Clear session and redirect to home

### 2. Book Catalog
- **Browse Books:** Grid layout of all available books
- **Book Cards:** Visual cards with cover images, title, author, genre
- **Availability Status:** Real-time status (Available/Borrowed)
- **Detailed View:** Modal/page view with full book information
- **Search/Filter:** Filter books by availability and genre (if implemented)

### 3. Book Management
- **Add New Book:** Form to create books with metadata
- **File Upload:** PDF upload support for book content
- **Edit Books:** Update book information
- **Delete Books:** Remove books from catalog
- **Book Details Page:** Dedicated page for each book with full information

### 4. Borrow/Return System
- **Borrow Books:** One-click borrow functionality
- **Return Books:** Return borrowed books
- **Borrow History:** Track user's borrowing activity
- **Status Updates:** Real-time UI updates on borrow/return actions
- **User Profile:** View borrowed books and history

### 5. Review System
- **Write Reviews:** Add reviews with star ratings (1-5)
- **View Reviews:** Display all reviews for a book
- **Rating Display:** Visual star rating system
- **Review Metadata:** Show reviewer name and timestamp
- **Sentiment Indicators:** Display LLM-generated sentiment analysis
- **Review Consensus:** AI-generated summary of all reviews

### 6. Recommendations
- **Personalized Recommendations:** ML-powered book suggestions based on user preferences and history
- **Similar Books:** Find books similar to ones you've enjoyed
- **Recommendation Cards:** Visual display of recommended books with explanations
- **Genre-based Suggestions:** Recommendations matched to user's favorite genres

### 7. User Profile
- **Profile Page:** View and edit user information
- **Preferences Management:** Set favorite genres for better recommendations
- **Borrowing History:** Complete history of borrowed and returned books
- **Update Profile:** Edit user preferences

### 8. UI/UX Features
- **Responsive Design:** Mobile-first, works on all screen sizes
- **Loading States:** Loading spinners for async operations
- **Error Handling:** User-friendly error messages
- **Toast Notifications:** Real-time feedback for user actions
- **Navigation Bar:** Consistent navigation with auth-aware menu
- **Dark Mode Ready:** Tailwind CSS configuration supports dark mode
- **Accessible:** Semantic HTML and ARIA labels

### 9. Testing
- **Unit Tests:** Component-level tests for critical UI components
- **Tested Components:**
  - `Nav` - Navigation bar with auth state
  - `BookCard` - Book display cards
  - `ErrorMessage` - Error display component
  - `LoadingSpinner` - Loading indicator
- **Test Coverage:** Jest and React Testing Library integration
- **CI-Ready:** Tests run via `npm test`

### 10. Performance Optimizations
- **Next.js App Router:** Modern routing with automatic code splitting
- **Server Components:** Leverage Next.js server components where applicable
- **Image Optimization:** Next.js Image component for optimized images (if used)
- **Font Optimization:** Built-in font optimization
- **Production Build:** Optimized build with minification and tree-shaking

## Project Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router pages
│   │   ├── books/
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx     # Book detail page (dynamic route)
│   │   │   ├── new/
│   │   │   │   └── page.tsx     # Add new book page
│   │   │   └── page.tsx         # Book catalog page
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── signup/
│   │   │   └── page.tsx         # Signup page
│   │   ├── profile/
│   │   │   └── page.tsx         # User profile page
│   │   ├── recommendations/
│   │   │   └── page.tsx         # Recommendations page
│   │   ├── layout.tsx           # Root layout with navigation
│   │   ├── page.tsx             # Home page
│   │   ├── error.tsx            # Error boundary
│   │   └── globals.css          # Global styles
│   ├── components/              # Reusable React components
│   │   ├── __tests__/           # Component tests
│   │   │   ├── Nav.test.tsx
│   │   │   ├── BookCard.test.tsx
│   │   │   ├── ErrorMessage.test.tsx
│   │   │   └── LoadingSpinner.test.tsx
│   │   ├── Nav.tsx              # Navigation bar
│   │   ├── BookCard.tsx         # Book card component
│   │   ├── BookViewModal.tsx    # Book detail modal
│   │   ├── ErrorMessage.tsx     # Error display component
│   │   ├── LoadingSpinner.tsx   # Loading indicator
│   │   └── Toaster.tsx          # Toast notification wrapper
│   └── lib/                     # Utilities and shared logic
│       ├── auth-context.tsx     # Authentication context provider
│       └── api.ts               # API client functions
├── public/                      # Static assets
├── .next/                       # Next.js build output (gitignored)
├── node_modules/                # Dependencies (gitignored)
├── jest.config.js               # Jest testing configuration
├── jest.setup.js                # Jest setup file
├── next.config.js               # Next.js configuration
├── next-env.d.ts                # Next.js TypeScript declarations
├── postcss.config.js            # PostCSS configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── Dockerfile                   # Docker container definition
├── package.json                 # Dependencies and scripts
└── package-lock.json            # Lockfile
```

## Setup & Running

### Using Docker (Recommended)
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

4. **Build for Production:**
   ```bash
   npm run build
   npm start
   ```

## Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run ESLint
npm run lint

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch
```

## Configuration

### Environment Variables

```bash
# API Backend URL (used in browser)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** `NEXT_PUBLIC_` prefix makes the variable available in the browser. Without it, the variable is only available during build time.

### Tailwind Configuration

See [tailwind.config.ts](tailwind.config.ts) for:
- Custom colors and theme
- Responsive breakpoints
- Dark mode settings
- Plugin configuration

### TypeScript Configuration

See [tsconfig.json](tsconfig.json) for:
- Path aliases (`@/` points to `src/`)
- Compiler options
- Type checking settings

## Code Quality

### Linting

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint -- --fix
```

ESLint is configured with Next.js recommended rules and TypeScript support.

### Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- Nav.test.tsx
```

Tests are written using Jest and React Testing Library. See `__tests__` directories for examples.

## API Integration

The frontend communicates with the backend via REST API. API client functions are in [src/lib/api.ts](src/lib/api.ts).

### Key API Functions:
- `login(email, password)` - Authenticate user
- `signup(email, password, name)` - Register new user
- `getBooks()` - Fetch all books
- `getBook(id)` - Fetch single book
- `createBook(data)` - Add new book
- `borrowBook(id)` - Borrow a book
- `returnBook(id)` - Return a book
- `addReview(bookId, data)` - Add review
- `getRecommendations()` - Get personalized recommendations

### Authentication Flow:
1. User logs in via `/auth/login`
2. Backend returns JWT token
3. Token stored in `localStorage`
4. Auth context manages global auth state
5. Token included in `Authorization` header for protected requests
6. On token expiry or error, user redirected to login

## Styling Guidelines

### Tailwind CSS Classes
- Use utility classes for most styling
- Create custom components for repeated patterns
- Use responsive modifiers (`sm:`, `md:`, `lg:`, etc.)
- Leverage Tailwind's color palette

### Example Component Styling:
```tsx
<div className="container mx-auto px-4 py-8">
  <h1 className="text-3xl font-bold text-gray-900 mb-6">
    Book Catalog
  </h1>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Book cards */}
  </div>
</div>
```

## Component Patterns

### Async Data Fetching
```tsx
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  fetchData()
    .then(setData)
    .catch(setError)
    .finally(() => setLoading(false));
}, []);

if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error.message} />;
return <DataDisplay data={data} />;
```

### Protected Routes
```tsx
'use client';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProtectedPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) return <LoadingSpinner />;
  if (!user) return null;

  return <YourContent />;
}
```

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## Performance Considerations

- **Code Splitting:** Next.js automatically splits code by route
- **Image Optimization:** Use Next.js `Image` component for automatic optimization
- **Font Loading:** Fonts loaded via Next.js font optimization
- **Bundle Size:** Monitor with `npm run build` output
- **Lazy Loading:** Dynamic imports for large components

## Accessibility

- Semantic HTML elements (`<nav>`, `<main>`, `<button>`, etc.)
- ARIA labels for interactive elements
- Keyboard navigation support
- Color contrast ratios meet WCAG AA standards
- Focus states for interactive elements

## Future Enhancements

Potential features to add:
- Advanced search and filtering
- Book categories/tags
- User avatars
- Reading lists/collections
- Social features (following users, sharing reviews)
- Reading progress tracking
- Book ratings aggregation
- Advanced analytics dashboard
- PWA support (offline functionality)
- Real-time notifications (WebSockets)

## Contributing

When adding new features:
1. Follow existing code patterns and structure
2. Write tests for new components
3. Use TypeScript for type safety
4. Follow Tailwind CSS conventions
5. Run linting and tests before committing
6. Update this README with new features

## Troubleshooting

### Common Issues

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running on the configured port
- Check CORS settings in backend

**Build errors:**
- Clear `.next` folder: `rm -rf .next`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npx tsc --noEmit`

**Test failures:**
- Clear Jest cache: `npm test -- --clearCache`
- Update snapshots: `npm test -- -u`

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
