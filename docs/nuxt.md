# Nuxt 3 Development Guide

## Content Management

### Querying Content with queryCollection

In this Nuxt 3 application, we use `queryCollection` to query content files from the `/content` directory. This is the modern way to access content in Nuxt 3 applications.

#### Basic Usage

```javascript
// Query all items from a collection
const data = await queryCollection('columns').find()

// Query a single item
const data = await queryCollection('columns').first()

// Query with filters
const data = await queryCollection('demographic_analysis')
  .where('target_column', 'GENHLTH')
  .first()
```

#### Content File Structure

Content files should be placed in the `/content` directory and can be:
- JSON files (`.json`)
- Markdown files (`.md`)
- YAML files (`.yaml`)

#### Individual vs Collection Files

For demographic analysis data, we have individual JSON files for each column:
- `/content/GENHLTH_demographic_analysis.json`
- `/content/FMONTH_demographic_analysis.json`

These files contain demographic analysis results with the following structure:
```json
{
  "target_column": "GENHLTH",
  "accuracy": 0.411,
  "classification_report": { ... },
  "feature_importance": [ ... ],
  "confusion_matrix": [ ... ],
  "class_labels": [ ... ],
  "model_parameters": { ... },
  "analysis_metadata": { ... }
}
```

### Common Patterns

1. **Loading individual analysis files**: Use file naming patterns to dynamically load content
2. **Error handling**: Always wrap content queries in try-catch blocks
3. **Loading states**: Use `useAsyncData` for proper loading and error states

### Migration Notes

- **DO NOT** use `queryContent()` - this is deprecated
- **USE** `queryCollection()` instead for all content querying
- Content files are automatically available as collections based on their location in `/content`