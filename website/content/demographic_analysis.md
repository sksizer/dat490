# Demographic Analysis Methodology

## Overview

This page describes the demographic analysis methodology used to evaluate how well demographic features can predict various health outcomes and behaviors in the BRFSS dataset.

## Purpose

The demographic analysis aims to understand which BRFSS survey responses can be reliably predicted from demographic information alone. This helps identify:
- Health disparities across demographic groups
- Potential biases in health outcomes
- Variables that show strong demographic patterns

## Methodology

### Machine Learning Model

We use a **Random Forest Classifier** to predict each BRFSS variable based on demographic features. Random Forest was chosen for its:
- Ability to handle mixed data types (numerical and categorical)
- Built-in feature importance metrics
- Robustness to overfitting
- No requirement for feature scaling

### Demographic Features Used

The analysis uses 26 demographic features from the BRFSS dataset, divided into two categories:

#### Direct Demographic Variables (13 features)
- `MARITAL` - Marital Status
- `EDUCA` - Education Level
- `RENTHOM1` - Own or Rent Home
- `NUMHHOL4` - Number of Adults in Household
- `NUMPHON4` - Number of Cell Phones
- `CPDEMO1C` - Demographics Module Available
- `VETERAN3` - Veteran Status
- `EMPLOY1` - Employment Status
- `CHILDREN` - Number of Children in Household
- `INCOME3` - Income Level
- `PREGNANT` - Pregnancy Status
- `WEIGHT2` - Reported Weight
- `HEIGHT3` - Reported Height

#### Calculated Demographic Variables (13 features)
- `_IMPRACE` - Imputed Race/Ethnicity
- `_CRACE1` - Calculated White/Black/Other Race
- `_MRACE1` - Calculated Multiracial
- `_RACE` - Calculated Race
- `_RACEG21` - Calculated Race Groups
- `_RACEGR3` - Calculated Race Grouping
- `_RACEPRV` - Calculated Race/Ethnicity
- `_SEX` - Calculated Sex
- `_AGEG5YR` - Calculated Age Groups (5-year)
- `_AGE65YR` - Calculated 65+ Age Groups
- `_AGE80` - Calculated Age 80+
- `_AGE_G` - Calculated Age Groups (6 levels)
- `_EDUCAG` - Calculated Education Level

### Analysis Process

1. **Data Preparation**
   - Load target variable and demographic features
   - Remove rows with missing target values
   - Remove features with >50% missing data
   - Filter columns with insufficient samples (<1000 valid responses)

2. **Model Training**
   - Split data into 80% training, 20% test sets
   - Train Random Forest with parameters:
     - `n_estimators`: 100
     - `max_depth`: 10
     - `min_samples_split`: 10
     - `min_samples_leaf`: 5
     - `random_state`: 42

3. **Evaluation Metrics**
   - **Accuracy**: Overall prediction accuracy on test set
   - **Classification Report**: Precision, recall, F1-score per class
   - **Feature Importance**: Relative importance of each demographic feature
   - **Confusion Matrix**: Actual vs predicted classifications

4. **Visualization Generation**
   - Confusion matrix heatmap
   - Feature importance bar chart
   - Both saved as SVG files for web display

### Interpretation

The **demographic analysis score** (accuracy) indicates how predictable a variable is from demographics alone:

- **High scores (>70%)**: Strong demographic patterns, potential health disparities
- **Medium scores (40-70%)**: Moderate demographic influence
- **Low scores (<40%)**: Weak demographic patterns, more individual variation

### Implementation

The analysis is implemented in `scripts/demographic_analysis.py` and can be run via:

```bash
python scripts/generate.py --demographic-analysis
```

This generates:
- Individual JSON files for each analyzed column in `/website/content/`
- Visualization SVGs in `/website/public/images/`
- Updated model.json with demographic analysis scores

### Limitations

- Analysis limited to variables with sufficient data (>1000 responses)
- Cannot capture complex interactions beyond Random Forest capabilities
- Results may be influenced by missing data patterns
- Demographic categories are as defined by BRFSS survey design