# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a BRFSS (Behavioral Risk Factor Surveillance System) data analysis and visualization platform with two main components:
1. Python data processing scripts that parse CDC codebook HTML and generate metadata
2. Nuxt 3 web application for interactive data exploration and visualization

## Commands

### Python/Data Processing (root directory)
```bash
# Install dependencies
poetry install

# Generate metadata from codebook
python generate.py

# Start Jupyter notebook
jupyter notebook
```

### Web Application
For frontend development commands and guidelines, see `web/README.md` and `web/CLAUDE.md`.

## Architecture

### Data Flow
1. `generate.py` processes the BRFSS codebook HTML (`data/codebook_USCODE23_LLCP_021924.HTML`)
2. Extracts column metadata and calculates statistics from `data/LLCP2023.parquet`
3. Generates `web/content/model.json` and `web/content/schema.json`
4. Web application reads these JSON files to power the interactive UI

### Key Components
- **generate.py**: Main data processing script using BeautifulSoup4, Pandas, and Pydantic
- **web/pages/columns/**: Interactive column browser with filtering and pandas code generation
- **web/components/**: Vue components for column management, filtering, and display
- **web/content/**: Markdown content and generated JSON data files

## Development Guidelines

### Python Code
- Use Poetry for dependency management
- Follow Pydantic models for data validation
- Process large parquet files efficiently with pandas
- Generate clean JSON output for web consumption

### Web Development
See `web/README.md` for setup instructions and `web/CLAUDE.md` for detailed development guidelines.

### Additional Documentation
- `docs/nuxt.md` - Nuxt 3 specific development patterns and content querying

## Important Files
- `/generate.py` - Main data processing script
- `/web/nuxt.config.ts` - Nuxt configuration
- `/web/pages/columns/index.vue` - Interactive column browser
- `/web/content/model.json` - Generated column metadata
- `/web/content/schema.json` - Generated column schema

## Common Issues and Solutions

### Scroll to Top Not Working
**Problem**: `window.scrollTo(0, 0)` doesn't work in Nuxt/Vue applications
**Cause**: Modern CSS frameworks use overflow containers for layout, not window-level scrolling
**Solution**: Reset scroll on multiple elements including CSS overflow containers:
```javascript
// Reset standard elements
document.documentElement.scrollTop = 0
document.body.scrollTop = 0
window.scrollTo(0, 0)

// Reset overflow containers
const containers = document.querySelectorAll('[style*="overflow"], .overflow-auto, .overflow-y-auto, .overflow-scroll, .overflow-y-scroll')
containers.forEach(container => container.scrollTop = 0)
```

### UTable Configuration Issues
**Problem**: "Columns require an id when using a non-string header"
**Cause**: UTable expects different column configurations for different use cases
**Solution**: Use simple HTML tables for basic display, or ensure proper column object structure with `id` property for UTable