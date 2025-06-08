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

The analysis uses 16 carefully selected demographic features from the BRFSS dataset:

#### Direct Demographic Variables (11 features)
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

#### Calculated Demographic Variables (5 features)
- `_HISPANC` - Hispanic/Latino Ethnicity (calculated)
- `_CRACE1` - Calculated White/Black/Other Race
- `_IMPRACE` - Imputed Race/Ethnicity
- `_SEX` - Calculated Sex
- `_AGE80` - Calculated Age 80+

#### Excluded Variables

The following variables were deliberately excluded from the demographic analysis to avoid obvious correlations with health outcomes:

- `WEIGHT2` and `HEIGHT3` - Physical measurements that directly relate to health conditions
- Additional race/ethnicity variables - To avoid redundancy with selected race variables

### Analysis Process

1. **Data Preparation**
   - Load target variable and 16 demographic features
   - Remove rows with missing target values
   - Drop features with >30% missing data (missing value threshold)
   - Fill remaining missing values with mode (most frequent value)
   - Filter target columns with insufficient samples (<1000 valid responses)
   - Exclude overly sparse categorical variables (>50% unique categories)
   - Require at least 2 unique values for classification

2. **Model Training**
   - Split data into 80% training, 20% test sets (stratified)
   - Train Random Forest with default parameters for efficiency:
     - `n_estimators`: 100 (number of trees)
     - `max_depth`: 10 (maximum tree depth)
     - `min_samples_split`: 10 (minimum samples to split)
     - `min_samples_leaf`: 5 (minimum samples per leaf)
     - `random_state`: 42 (for reproducibility)
     - `hyperparameter_tuning`: False (disabled for bulk analysis performance)

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

The analysis is implemented in `scripts/demographic_analysis.py` and orchestrated via `scripts/generate.py`. 

#### Running the Analysis

```bash
# Full analysis (all applicable columns)
python scripts/generate.py --demographic-analysis

# Test mode (limited to GENHLTH, ASTHMS1, MICHD)
python scripts/generate.py --demographic-analysis --test-mode

# Sequential processing (for debugging)
python scripts/generate.py --demographic-analysis --sequential

# Parallel processing with custom worker count
python scripts/generate.py --demographic-analysis --max-workers 8
```

#### Performance Features

- **Parallel Processing**: Uses ProcessPoolExecutor for concurrent analysis
- **Memory Optimization**: Each worker loads its own data copy to avoid memory sharing issues
- **Automatic Filtering**: Only analyzes columns meeting data quality criteria
- **Progress Tracking**: Real-time logging of analysis progress and results

#### Generated Output

This generates:
- Individual JSON files for each analyzed column in `/website/content/`
- Confusion matrix and feature importance SVGs in `/website/public/images/`
- Updated model.json with demographic analysis scores embedded

### Limitations

- Analysis limited to variables with sufficient data (>1000 responses)
- Cannot capture complex interactions beyond Random Forest capabilities
- Results may be influenced by missing data patterns
- Demographic categories are as defined by BRFSS survey design