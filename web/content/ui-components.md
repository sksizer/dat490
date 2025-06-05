---
title: Nuxt UI Components 
description: Documentation of available Nuxt UI components and usage notes
navigation:
  title: UI Components
  icon: i-heroicons-puzzle-piece
  order: 3
---

# Nuxt UI Components

This page documents the available Nuxt UI components for the DAT490 project and provides usage notes.

## Available Components

Nuxt UI provides a set of pre-built components. The ones we're using in this project include:

- `UButton` - Buttons with various styles and variants
- `UContainer` - Container for layout content
- `UDropdownMenu` - Dropdown menu with support for nested items
- `UNavigationTree` - Navigation component for displaying hierarchical links

## Not Available Components

The following are not actual Nuxt UI components and should be implemented with standard HTML:

- ❌ `UHeader` - Use standard `<header>` with custom styling instead
- ❌ `UFooter` - Use standard `<footer>` with custom styling instead

## Usage Examples

### Dropdown Menu

```vue
<UDropdownMenu :items="menuItems" hover>
  <UButton color="white" variant="ghost" icon="i-heroicons-bars-3-20-solid" />
</UDropdownMenu>
```

Where `menuItems` is an array with this structure:

```ts
const menuItems = [
  { label: 'Home', to: '/', icon: 'i-heroicons-home' },
  { 
    label: 'Documentation', 
    icon: 'i-heroicons-book-open',
    children: [
      { label: 'Getting Started', to: '/docs/getting-started' }
    ]
  }
]
```

## Resources

- [Nuxt UI Documentation](https://ui.nuxt.com/components) - Official component documentation
- [Nuxt Content Documentation](https://content.nuxt.com/docs/utils/query-collection) - For content queries