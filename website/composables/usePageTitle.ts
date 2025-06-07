/**
 * Composable for managing breadcrumbs in the TopBar
 */

interface BreadcrumbItem {
  label: string
  to?: string
  icon?: string
}

export const usePageTitle = () => {
  // Use Nuxt's useState to create reactive state that persists across component boundaries
  const pageTitle = useState<string>('pageTitle', () => '')
  const breadcrumbs = useState<BreadcrumbItem[]>('breadcrumbs', () => [])
  
  // Function to set the page title from any component (legacy support)
  const setPageTitle = (title: string) => {
    pageTitle.value = title
  }
  
  // Function to clear the page title (back to default)
  const clearPageTitle = () => {
    pageTitle.value = ''
  }
  
  // Function to set breadcrumbs
  const setBreadcrumbs = (items: BreadcrumbItem[]) => {
    breadcrumbs.value = items
  }
  
  // Function to clear breadcrumbs
  const clearBreadcrumbs = () => {
    breadcrumbs.value = []
  }
  
  return {
    pageTitle: readonly(pageTitle),
    breadcrumbs: readonly(breadcrumbs),
    setPageTitle,
    clearPageTitle,
    setBreadcrumbs,
    clearBreadcrumbs
  }
}