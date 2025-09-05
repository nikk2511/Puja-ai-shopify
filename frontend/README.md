# Puja AI Shopify Frontend

This is the Next.js frontend for the Puja AI Shopify Chatbot, providing both a standalone web application and an embeddable widget for Shopify stores.

## Features

- **Next.js 14** with App Router
- **Tailwind CSS** for styling
- **Shopify App Bridge** integration
- **Responsive Design** for all devices
- **Embeddable Widget** for any website
- **Real-time AI Chat** with structured responses
- **Product Integration** with Shopify links

## Quick Start

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set environment variables:**
   ```bash
   # Create .env.local file
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:3000
   ```

### Production Build

```bash
npm run build
npm start
```

## Integration Options

### 1. Standalone Web Application

Deploy the Next.js app to Vercel, Netlify, or any hosting platform:

```bash
# Deploy to Vercel
npx vercel

# Or build for static hosting
npm run build
npm run export
```

### 2. Embeddable Widget

Use the embeddable widget (`public/embed.js`) in any website:

#### Basic Integration

```html
<!-- Add to your HTML -->
<script src="https://your-domain.com/embed.js"></script>
<div id="puja-ai-widget"></div>
```

#### Advanced Configuration

```html
<script>
  window.pujaAIConfig = {
    apiUrl: 'https://your-backend.com',
    theme: 'light',
    position: 'bottom-right',
    autoOpen: false
  };
</script>
<script src="https://your-domain.com/embed.js"></script>
```

#### Shopify Theme Integration

1. **Via Theme Editor:**
   - Go to Shopify Admin → Online Store → Themes
   - Edit Code → `layout/theme.liquid`
   - Add before `</body>`:
   ```liquid
   <script src="https://your-domain.com/embed.js"></script>
   ```

2. **Via Script Tag API:**
   ```javascript
   // Use Shopify Script Tag API to inject the widget
   POST /admin/api/2023-10/script_tags.json
   {
     "script_tag": {
       "event": "onload",
       "src": "https://your-domain.com/embed.js"
     }
   }
   ```

### 3. Shopify Embedded App

For full Shopify app integration:

1. **Create Shopify Partner account**
2. **Create new app in Partner Dashboard**
3. **Set app URL** to your deployed frontend
4. **Configure OAuth** (see Shopify App Bridge documentation)

## Components

### Core Components

- **`PujaWidget.jsx`** - Main chatbot interface
- **`PresetButtons.jsx`** - Pre-configured puja options
- **`ChatInput.jsx`** - Text input with validation
- **`AnswerDisplay.jsx`** - Structured response display

### Component Usage

```jsx
import PujaWidget from './components/PujaWidget'

function MyPage() {
  return (
    <div>
      <PujaWidget isEmbedded={false} />
    </div>
  )
}
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS with custom design tokens:

```css
/* Custom colors */
--puja-orange: #FF6B35
--puja-red: #D73027
--puja-gold: #FFD700

/* Usage */
.puja-gradient {
  @apply bg-gradient-to-r from-puja-orange to-puja-red;
}
```

### Custom CSS Classes

- `.puja-button-primary` - Primary action buttons
- `.puja-button-secondary` - Secondary buttons
- `.puja-card` - Content cards
- `.preset-button` - Preset selection buttons

## API Integration

### Environment Variables

```bash
# Required
NEXT_PUBLIC_API_URL=https://your-backend.com

# Optional
NEXT_PUBLIC_SHOPIFY_APP_KEY=your_app_key
NEXT_PUBLIC_ENVIRONMENT=production
```

### API Endpoints Used

- `GET /api/presets` - Fetch available puja presets
- `POST /api/ask` - Submit questions and get responses
- `GET /api/health` - Backend health check

## Deployment

### Vercel (Recommended)

1. **Connect GitHub repository**
2. **Set environment variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.com
   ```
3. **Deploy automatically on push**

### Netlify

```bash
# Build command
npm run build

# Publish directory
out
```

### Traditional Hosting

```bash
# Build static files
npm run build
npm run export

# Upload 'out' directory to your host
```

## Shopify Integration Guide

### Method 1: Theme Integration (Simplest)

1. **Upload widget file:**
   - Upload `public/embed.js` to your CDN or hosting
   
2. **Edit theme code:**
   ```liquid
   <!-- In theme.liquid before </body> -->
   <script>
     window.pujaAIConfig = {
       apiUrl: '{{ shop.metafields.pujaai.api_url | default: "https://your-backend.com" }}',
       theme: '{{ shop.metafields.pujaai.theme | default: "light" }}'
     };
   </script>
   <script src="https://your-cdn.com/embed.js"></script>
   ```

3. **Add container (optional):**
   ```liquid
   <!-- In any template where you want inline widget -->
   <div id="puja-ai-widget"></div>
   ```

### Method 2: Script Tag API

```javascript
// Install via Shopify API
curl -X POST "https://your-shop.myshopify.com/admin/api/2023-10/script_tags.json" \
  -H "X-Shopify-Access-Token: YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "script_tag": {
      "event": "onload",
      "src": "https://your-domain.com/embed.js"
    }
  }'
```

### Method 3: Shopify App (Advanced)

1. **Create Shopify Partner account**
2. **Create new app:**
   ```
   App URL: https://your-frontend.vercel.app
   Allowed redirection URLs: https://your-frontend.vercel.app/auth/callback
   ```

3. **Implement OAuth flow:**
   ```javascript
   // In your Next.js app
   import { useAuthenticatedFetch } from '@shopify/app-bridge-react'
   
   function App() {
     const fetch = useAuthenticatedFetch()
     // Your app logic
   }
   ```

## Customization

### Theming

```javascript
// Custom theme configuration
window.pujaAIConfig = {
  theme: {
    primaryColor: '#FF6B35',
    secondaryColor: '#D73027',
    fontFamily: 'Inter, sans-serif',
    borderRadius: '8px'
  }
}
```

### Custom Presets

```javascript
// Override default presets
window.pujaAIConfig = {
  customPresets: [
    {
      id: 'custom_puja',
      name: 'Custom Puja',
      description: 'My custom puja guidance'
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   ```javascript
   // Ensure backend allows your domain
   // Check NEXT_PUBLIC_API_URL is correct
   ```

2. **Shopify CSP Issues:**
   ```liquid
   <!-- Add to theme.liquid <head> -->
   <meta http-equiv="Content-Security-Policy" 
         content="script-src 'self' 'unsafe-inline' https://your-domain.com;">
   ```

3. **Mobile Responsive Issues:**
   ```css
   /* Widget automatically adjusts, but you can override */
   @media (max-width: 480px) {
     .puja-ai-widget {
       width: calc(100vw - 20px) !important;
     }
   }
   ```

### Debug Mode

```javascript
// Enable debug mode
window.pujaAIConfig = {
  debug: true
}

// Check console for detailed logs
```

## Performance

### Optimization Tips

1. **Lazy loading:**
   ```javascript
   // Widget loads on first interaction
   // No impact on initial page load
   ```

2. **Bundle size:**
   ```bash
   # Check bundle size
   npm run build
   npm run analyze
   ```

3. **CDN usage:**
   ```html
   <!-- Use CDN for faster loading -->
   <script src="https://cdn.jsdelivr.net/gh/yourusername/yourrepo@main/frontend/public/embed.js"></script>
   ```

## Development

### Local Development with Backend

```bash
# Terminal 1: Start backend
cd ../backend
uvicorn app:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Testing

```bash
# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Test in different browsers
npm run dev
```

## Support

For issues and support:

1. Check the troubleshooting section above
2. Review the backend API documentation
3. Check browser console for errors
4. Ensure CORS and CSP policies are configured correctly

## License

This project is part of the Puja AI Shopify Chatbot system. See main README for license information.
