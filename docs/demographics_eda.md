# Demographic Analysis - BRFSS 2023



## Overview

We performed an exploratory prediction of multiple features by a selected set
of demographic features from the BRFSS 2023 dataset. 

Our primary goal is to focus on understanding how demographic factors impact
various other personal health factors such as chronic disease prevalence, health
care access, etc. 

This analysis was done as a preliminary exploratory step using the fairly 
inexpensive Random Forest algorithm. Given the computational ease we could
do this we ran a predication against all appropriate available features
numbering (186) in the BRFSS 2023 dataset.

## Demographic Features

Our analysis uses 16 core demographic features from the BRFSS dataset:

| Feature | Description | Type | Link |
|---------|-------------|------|------|
| [MARITAL](https://singular-eclair-6a5a16.netlify.app/columns/MARITAL) | Marital status | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/MARITAL) |
| [EDUCA](https://singular-eclair-6a5a16.netlify.app/columns/EDUCA) | Education level | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/EDUCA) |
| [RENTHOM1](https://singular-eclair-6a5a16.netlify.app/columns/RENTHOM1) | Home ownership | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/RENTHOM1) |
| [NUMHHOL4](https://singular-eclair-6a5a16.netlify.app/columns/NUMHHOL4) | Household size | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/NUMHHOL4) |
| [NUMPHON4](https://singular-eclair-6a5a16.netlify.app/columns/NUMPHON4) | Phone access | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/NUMPHON4) |
| [CPDEMO1C](https://singular-eclair-6a5a16.netlify.app/columns/CPDEMO1C) | Cell phone demographics | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/CPDEMO1C) |
| [VETERAN3](https://singular-eclair-6a5a16.netlify.app/columns/VETERAN3) | Military service | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/VETERAN3) |
| [EMPLOY1](https://singular-eclair-6a5a16.netlify.app/columns/EMPLOY1) | Employment status | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/EMPLOY1) |
| [CHILDREN](https://singular-eclair-6a5a16.netlify.app/columns/CHILDREN) | Number of children | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/CHILDREN) |
| [INCOME3](https://singular-eclair-6a5a16.netlify.app/columns/INCOME3) | Income level | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/INCOME3) |
| [PREGNANT](https://singular-eclair-6a5a16.netlify.app/columns/PREGNANT) | Pregnancy status | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/PREGNANT) |
| [SEXVAR](https://singular-eclair-6a5a16.netlify.app/columns/SEXVAR) | Sex variable | Survey | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/SEXVAR) |
| [_HISPANC](https://singular-eclair-6a5a16.netlify.app/columns/_HISPANC) | Hispanic/Latino ethnicity | Calculated | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/_HISPANC) |
| [_CRACE1](https://singular-eclair-6a5a16.netlify.app/columns/_CRACE1) | Child race category | Calculated | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/_CRACE1) |
| [_IMPRACE](https://singular-eclair-6a5a16.netlify.app/columns/_IMPRACE) | Imputed race/ethnicity | Calculated | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/_IMPRACE) |
| [_AGE80](https://singular-eclair-6a5a16.netlify.app/columns/_AGE80) | Age 80+ indicator | Calculated | [View Details](https://singular-eclair-6a5a16.netlify.app/columns/_AGE80) |

**Summary**: 12 survey demographics + 4 calculated demographics = 16 total features

## Analysis Methodology

### Machine Learning Approach
- **Algorithm**: Random Forest Classifier
- **Target Variables**: Health outcome and various individual status columns from BRFSS dataset
- **Feature Set**: 16 demographic variables (target column was automatically excluded to avoid data leakage)
- **Data Requirements**: Minimum 1,000 data points per analysis

### Data Preprocessing
- **Feature Selection**: Used only demographic features, and minimized calculated features to avoid data leakage. Also excluded weight and height features under assumption they may have an overwhelming impact on health outcomes.
- **Semantic Null Handling**: Convert coded missing values (7, 9, 77, 99, etc.) to NaN
- **Feature Filtering**: Remove features with >30% missing values
- **Target Exclusion**: Automatically exclude target variable from feature set
- **Missing Value Imputation**: We filled in remaining missing values with mode for each feature
- **Class Balance**: Use stratified sampling in train/test split to maintain class proportions

### Model Evaluation
- **Primary Metric**: Classification accuracy
- **Additional Metrics**: Precision, recall, F1-score
- **Cross-validation**: model validation
- **Visualizations**: Confusion matrices and feature importance plots

## Caveats and Limitations
Much of the data has highly imbalanced categories, so using accuracy as primary metric 
for visualization was not ideal. However, given the exploratory nature of this it
was deemed sufficient for this initial analysis.

We did no additional hyperparameter tuning.

## Key Findings

### Predictive Power Distribution
Analysis reveals varying levels of demographic predictability across health outcomes:

![Demographic Analysis Overview](placeholder-demographic-overview.png)
*Screenshot: Main demographic analysis page showing accuracy distribution across all analyzed features*

- **High Predictability (>80% accuracy)**: Some health behaviors and access variables
- **Moderate Predictability (60-80% accuracy)**: Many chronic conditions and screening behaviors
- **Low Predictability (<60% accuracy)**: Acute health events and specific symptoms

![Feature Importance Rankings](placeholder-feature-importance-rankings.png)
*Screenshot: Top demographic predictors ranked by average importance across all models*

### Feature Importance Patterns
Demographic features show consistent importance patterns:

- **Age Variables**: Strong predictors across most health outcomes
- **Income and Education**: Significant predictors for preventive care and chronic conditions
- **Race/Ethnicity**: Important for health disparities analysis

![Individual Feature Analysis](placeholder-individual-feature-analysis.png)
*Screenshot: Example individual feature analysis page (GENHLTH) showing confusion matrix and feature importance*

### Health Disparities Insights
The analysis reveals demographic patterns in health outcomes:

- **Socioeconomic Factors**: Income and education strongly predict healthcare access
- **Age-Related Patterns**: Unsurprisingly age-based health outcome predictions
- **Racial/Ethnic Disparities**: Systematic differences in health outcomes by race/ethnicity OTHER than 'Hispanic' categorization

## Technical Implementation

### Data Quality Requirements
- **Minimum Sample Size**: 1,000 respondents per analysis
- **Feature Completeness**: Exclude features with excessive missing data
- **Target Validation**: Ensure sufficient class representation

### Performance Optimization
- **Parallel Processing**: Multiple analyses run concurrently
- **Progress Tracking**: Real-time analysis completion monitoring
- **Error Handling**: Robust handling of edge cases and data quality issues

### Output Generation
- **Analysis Results**: JSON files with complete model metrics
- **Visualizations**: SVG format confusion matrices and feature importance plots
- **Metadata Integration**: Accuracy scores integrated into column metadata

## Applications and Use Cases

![Column Browser Integration](placeholder-column-browser-integration.png)
*Screenshot: Main column browser showing demographic analysis scores integrated into the feature table*

### Research Applications
- **Health Disparities Research**: Identify demographic groups at risk
- **Predictive Modeling**: Baseline demographic predictability assessment
- **Feature Selection**: Identify important demographic predictors

### Public Health Applications
- **Targeted Interventions**: Focus resources on high-risk demographic groups
- **Health Equity Assessment**: Quantify demographic health disparities
- **Policy Planning**: Evidence-based policy development

![Interactive Visualizations](placeholder-interactive-visualizations.png)
*Screenshot: Interactive charts showing model performance and feature importance with hover details*

### Data Science Applications
- **Model Benchmarking**: Demographic predictability as baseline
- **Feature Engineering**: Understand demographic feature importance
- **Data Quality Assessment**: Identify patterns in missing data

## Limitations and Considerations

### Data Limitations
- **Cross-sectional Data**: No causal inference possible
- **Self-reported Data**: Potential reporting bias
- **Missing Data**: Skip logic creates systematic missingness

### Methodological Limitations
- **Model Choice**: Random Forest may not capture all relationships
- **Feature Set**: Limited to 16 available demographic variables
- **Temporal Factors**: No time-series analysis
- **Class Imbalance**: Only stratified sampling used; no advanced rebalancing techniques
- **Missing Data**: Simple mode imputation may not capture complex patterns

### Interpretation Caveats
- **Correlation vs. Causation**: Results show association, not causation
- **Population Representativeness**: BRFSS sampling considerations
- **Demographic Complexity**: Simplified demographic categories

## Future Directions

### Enhanced Analysis
- **Multiple Algorithms**: Compare Random Forest with other ML methods
- **Interaction Effects**: Explore demographic feature interactions
- **Temporal Analysis**: Longitudinal demographic patterns

### Expanded Applications
- **Subgroup Analysis**: Detailed analysis within demographic groups
- **Geographic Modeling**: State and regional demographic patterns
- **Intervention Targeting**: Demographic-based intervention strategies

This demographic analysis provides a comprehensive foundation for understanding how demographic characteristics relate to health outcomes in the BRFSS 2023 dataset, enabling evidence-based research and policy development.