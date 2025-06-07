# Demographic Analysis Feature PRD

## Overview

This PRD outlines the implementation of a comprehensive demographic analysis feature for the BRFSS data browser. The feature will perform Random Forest machine learning analysis to predict each column's values based on demographic features, providing predictive insights into the relationship between demographics and health outcomes.

## Goals and Objectives

### Primary Goals
- Enable automated demographic analysis for all applicable BRFSS columns
- Provide machine learning insights into demographic predictors of health outcomes
- Create interactive visualizations of analysis results
- Maintain performance and scalability of the data browser

### Success Metrics
- Successful analysis generation for 80%+ of applicable columns
- Analysis accuracy scores available in column metadata
- Interactive visualizations displaying properly in column detail pages
- Documentation providing clear methodology explanation

## User Stories

### Data Researcher
- **As a researcher**, I want to see how well demographics predict a health outcome, so I can understand demographic risk factors
- **As a researcher**, I want to compare demographic predictive power across different health variables
- **As a researcher**, I want to see which demographic features are most important for each health outcome

### Data Analyst
- **As an analyst**, I want sortable demographic analysis scores in the column browser
- **As an analyst**, I want interactive visualizations showing model performance and feature importance
- **As an analyst**, I want to understand the methodology behind the analysis

## Technical Requirements

### Core Functionality

#### 1. Demographic Analysis Function
- Convert existing Random Forest notebook code into reusable function
- Use semantic null handling for clean data preprocessing
- Generate accuracy scores, confusion matrices, and feature importance
- Handle edge cases (insufficient data, inappropriate targets, etc.)

#### 2. Data Model Updates
- Add `demographic_analysis_score` field to `ColumnMetadata` Pydantic model
- Create comprehensive `DemographicAnalysis` Pydantic model for analysis results
- Update Zod schema in `website/content.config.ts`

#### 3. Analysis Generation
- Integrate analysis function into `scripts/generate.py`
- Run analysis for all applicable columns during data generation
- Save individual analysis results as JSON files
- Generate visualization images (confusion matrix, feature importance)

#### 4. Website Integration
- Add sortable "Demographic Analysis" column to columns table
- Create "Demographic Analysis" section in column detail pages
- Display analysis images and interactive Vue ECharts
- Add methodology documentation and linking

### Technical Specifications

#### Feature Columns (Configurable)
```python
# In scripts/generate.py
# Demographics feature columns - automatically excludes target column during analysis
DEMOGRAPHIC_FEATURE_COLUMNS = [
    # Demographics section columns (13 total)
    'MARITAL', 'EDUCA', 'RENTHOM1', 'NUMHHOL4', 'NUMPHON4', 'CPDEMO1C', 
    'VETERAN3', 'EMPLOY1', 'CHILDREN', 'INCOME3', 'PREGNANT', 'WEIGHT2', 'HEIGHT3',
    
    # Calculated demographic variables (13 total) 
    '_IMPRACE', '_CRACE1', '_MRACE1', '_RACE', '_RACEG21', '_RACEGR3', '_RACEPRV', 
    '_SEX', '_AGEG5YR', '_AGE65YR', '_AGE80', '_AGE_G', '_EDUCAG'
]

# Note: Target column will be automatically excluded from features during analysis
# Columns with >30% missing values will be filtered out during preprocessing
```

#### Data Structures

##### ColumnMetadata Update
```python
class ColumnMetadata(BaseModel):
    # ... existing fields ...
    demographic_analysis_score: Optional[float] = None
```

##### DemographicAnalysis Model
```python
class DemographicAnalysis(BaseModel):
    target_column: str
    accuracy: float
    classification_report: dict
    feature_importance: List[Dict[str, Union[str, float]]]
    confusion_matrix: List[List[int]]
    class_labels: List[str]
    model_parameters: dict
    analysis_metadata: dict
```

#### File Structure
```
website/content/
├── model.json                          # Updated with demographic_analysis_scores
├── schema.json                         # Updated schema
├── <COLUMN>_demographic_analysis.json  # Individual analysis results
└── demographic_analysis.md             # Methodology documentation

website/public/images/
├── <COLUMN>_demographic_analysis_confusion_matrix.svg
└── <COLUMN>_demographic_analysis_feature_importance.svg
```

## Implementation Phases

### Phase 1: Core Infrastructure ⭐ **START HERE**
**Duration**: 1-2 days  
**Goal**: Set up foundation and test with single column

#### Tasks
- [ ] Add `demographic_analysis_score` to `ColumnMetadata` Pydantic model
- [ ] Update Zod schema in `website/content.config.ts`
- [ ] Add "Demographic Analysis" column to columns table (after Column/Feature)
- [ ] Convert Random Forest notebook code to reusable function
- [ ] Add configurable `DEMOGRAPHIC_FEATURE_COLUMNS` constant to `scripts/generate.py`
- [ ] Test function with GENHLTH column

#### Acceptance Criteria
- New column appears in website table (initially empty/null)
- Demographic analysis function successfully predicts GENHLTH
- Function returns accuracy score and key metrics
- No breaking changes to existing functionality

### Phase 2: Data Model and Schema
**Duration**: 1 day  
**Goal**: Define comprehensive data structure

#### Tasks
- [ ] Create `DemographicAnalysis` Pydantic model
- [ ] Generate JSON schema for analysis results
- [ ] Test serialization/deserialization with sample data
- [ ] Update website content.config.ts with new schema

#### Acceptance Criteria
- Well-defined data model for all analysis results
- JSON schema validates correctly
- Successful serialization of sample analysis

### Phase 3: Analysis Generation
**Duration**: 2-3 days  
**Goal**: Generate analysis for all applicable columns

#### Tasks
- [ ] Integrate demographic analysis into `scripts/generate.py`
- [ ] Implement analysis filtering logic:
  - Minimum 1000 data points for analysis viability
  - Exclude categorical columns (if any)
  - Target column automatically excluded from feature set
- [ ] Generate individual JSON files for each analysis
- [ ] Create visualization generation (prioritize SVG format for space efficiency)
- [ ] Update `ColumnMetadata` with analysis scores
- [ ] Implement parallel processing with progress indicators
- [ ] Add time tracking for analysis components in `scripts/generate.py`
- [ ] Implement error handling and logging

#### Acceptance Criteria
- Analysis runs for all applicable columns (minimum 1000 data points each)
- Individual JSON files created for each analysis
- SVG visualizations generated (space-efficient format)
- Column metadata updated with scores
- Parallel processing implemented with progress tracking
- Time tracking shows analysis component duration
- Comprehensive error handling

### Phase 4: Website Integration
**Duration**: 2 days  
**Goal**: Display analysis results in web interface

#### Tasks
- [ ] Update column detail pages with Demographic Analysis section
- [ ] Display generated SVG images
- [ ] Create Vue ECharts components from JSON data
- [ ] Add conditional rendering (only show if analysis exists)
- [ ] Implement methodology documentation linking
- [ ] Add question mark icon link to `/demographic_analysis`

#### Acceptance Criteria
- Demographic Analysis section appears on applicable column pages
- Visualizations display correctly
- Interactive charts work properly
- Documentation links function
- Clean UI for columns without analysis

### Phase 5: Documentation and Polish
**Duration**: 1 day  
**Goal**: Complete documentation and testing

#### Tasks
- [ ] Write comprehensive methodology documentation
- [ ] Test full end-to-end workflow
- [ ] Performance optimization if needed
- [ ] User acceptance testing
- [ ] Final bug fixes and polish

#### Acceptance Criteria
- Complete methodology documentation
- All features working end-to-end
- No performance regressions
- Clean, intuitive user experience

## Technical Considerations

### Performance
- Analysis generation may be time-intensive for large numbers of columns
- Parallel processing implemented with progress indicators showing completion status
- Time tracking implemented to monitor analysis component duration
- Progress logging and error recovery implemented

### Data Quality
- Minimum 1000 data points required for reliable analysis
- Categorical columns excluded from analysis scope
- Target column automatically excluded from feature set during analysis
- Handle edge cases (columns with insufficient variation, etc.)
- Graceful degradation when analysis isn't appropriate

### Scalability
- File-based storage for analysis results allows easy caching
- SVG images provide scalable, space-efficient visualizations (prioritized over PNG/JPG)
- JSON structure allows easy extension for future analysis types
- Parallel processing scales analysis generation across multiple columns

## Risk Assessment

### High Risk
- **Performance Impact**: Running ML analysis on all columns could be slow
  - *Mitigation*: Implement parallel processing with progress indicators and time tracking

### Medium Risk
- **Data Quality Issues**: Some columns may not be suitable for demographic analysis
  - *Mitigation*: Implement robust filtering (minimum 1000 data points, exclude categorical columns) and error handling
- **UI Complexity**: Adding analysis sections could clutter column pages
  - *Mitigation*: Use conditional rendering and clean design

### Low Risk
- **Schema Changes**: Updates to data models could break existing functionality
  - *Mitigation*: Careful testing and backwards compatibility

## Success Criteria

### Technical Success
- [ ] Analysis generates successfully for 80%+ of applicable columns
- [ ] No performance regressions in existing functionality
- [ ] All visualizations render correctly
- [ ] Comprehensive error handling and logging

### User Experience Success
- [ ] Intuitive navigation and discovery of analysis results
- [ ] Clear, understandable visualizations
- [ ] Helpful methodology documentation
- [ ] Fast page load times despite additional content

### Business Success
- [ ] Enhanced research capabilities for BRFSS data users
- [ ] Increased user engagement with demographic insights
- [ ] Platform differentiation through ML-powered analysis

## Dependencies

### Technical Dependencies
- Random Forest implementation from existing notebook
- SVG generation capabilities (matplotlib, plotly)
- Vue ECharts integration
- Pydantic model updates

### Resource Dependencies
- Computational resources for analysis generation
- Storage for analysis results and visualizations
- Testing time for comprehensive validation

## Future Enhancements

### Potential Extensions
- Multiple ML algorithms (Logistic Regression, Gradient Boosting)
- Time-series analysis for longitudinal data
- Interactive model parameter adjustment
- Comparison analysis between different demographic groups
- Export capabilities for analysis results

### Integration Opportunities
- Connection with external research databases
- Integration with statistical analysis packages
- API endpoints for programmatic access
- Real-time analysis updates

---

## Implementation Notes

This PRD provides a structured approach to implementing demographic analysis. Each phase has clear deliverables and can be validated independently, allowing for course correction if needed.

The phased approach ensures we can deliver value incrementally while maintaining system stability and performance.

## Questions for Resolution

1. ✅ **Feature Column Selection**: Confirmed demographic feature set (26 features, target column automatically excluded)
2. ✅ **Analysis Scope**: Exclude categorical columns, minimum 1000 data points
3. ✅ **Minimum Data Requirements**: 1000 data points minimum for analysis viability
4. ✅ **Performance Targets**: Parallel processing with progress indicators and time tracking
5. ✅ **Visualization Format**: Prioritize SVG format for space efficiency
6. **UI/UX Preferences**: Confirm design direction for analysis display

---

*Last Updated: [Current Date]*  
*Status: Ready for Implementation*