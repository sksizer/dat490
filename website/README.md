# DAT490 Web Application

This project is built with:
- [Nuxt 3](https://nuxt.com) - The Vue.js Framework
- [Nuxt Content 3](https://content.nuxt.com) - Document-driven mode for content
- [Nuxt UI](https://ui.nuxt.com) - Component library for Nuxt

Look at the [Nuxt documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

## Project Structure

- `/pages` - All pages/routes of the application
- `/components` - Reusable Vue components
- `/layouts` - Page layouts with common elements
- `/content` - Markdown content files for Nuxt Content
- `/assets` - Static assets like CSS, images, and fonts
- `/public` - Static files served at root level

## Development Guidelines

- We use Nuxt UI components first and foremost
- All components should be written using Vue 3 Composition API with `<script setup>` syntax
- For detailed styling and code guidelines, refer to `CLAUDE.md`
