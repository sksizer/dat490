# Exploratory Data Analysis - BRFSS 2023

## Dataset Overview

The Behavioral Risk Factor Surveillance System (BRFSS) is the nation's premier system of health-related telephone surveys. The dataset is one of the most comprehensive health surveys in the United States.

This analysis focuses on the 2023 BRFSS dataset. It includes responses from over 400,000 individuals, and encompasses all states and territories.

## Data Source

We sourced codebook and data directly from the CDC's data site at [CDC BRFSS 2023](https://www.cdc.gov/brfss/annual_data/annual_2023.html).

### Dataset

The data is provided in two different formats:
- an ASCII format that has 2011 columns
- SAS Transport Format that had 344 columns. 

We chose to start from the SAS Transport Format as it was better structured less duplicative columns and would be easier to tailor to our needs. 

#### Dataset Dimensions

| Metric                | Value                                                      |
|-----------------------|------------------------------------------------------------|
| Total Columns         | 344 (survey questions, calculated variables, weights); 6 undocumented columns remain present in data |
| Respondent Count      | 433,323 respondents across all US states and territories   |
| Thematic Sections     | 58 thematic sections organizing health topics              |
| Computed Columns      | 76 computed columns derived from survey responses          |
| Direct Survey Questions | 268 direct survey questions                              |

### Codebook

There are several supplementary files provided by the CDC that provided extensive documentation such as
- survey methodology
- survey and data architecture
- document data file
- statistical weighting procedures
- calculated variable formulas
- documentation of data values to semantic meaning 

The most helpful amongst these was the [HTML Codebook](https://singular-eclair-6a5a16.netlify.app/html/codebook_uscode23_llcp_021924) which presented feature information in a very consistent way which was easy to parse and extract into our own structured model to apply to the data. This codebook provided structured metadata for each column in the dataset. 

The most important component of this was the semantic mapping of particular column/feature values. 


## Data Preparation

### Data Format

The dataset was provided in SAS Transport Format, which we converted to Parquet format for a more familiar format and smaller filesize. 

### Value Semantics
The majority of the variable/features in the dataset are coded with numeric values that correspond to some other semantic meaning such as:
- Yes/No responses
- Missing data indicators
- Categorical responses
- Categorical values derived from multiple responses

#### Missing Data Handling

Missing data could be expressed in two ways - as null/NaN values or as specific numeric codes. 

These numeric codes were not standardized across columns - the particular value depended on the cardinality of possible answers, or minor semantic differences (such as missing/refused/no answer).

*Examples*

| Code    | Meaning                        |
|---------|-------------------------------|
| `7`     | Don\`t know/Not sure           |
| `9`     | Refused                       |
| `77`, `99` | Extended codes for multi-digit responses |
| `BLANK` | Not asked or Missing          |



Fortunately the aforementioned HTML BRFSS Codebook made it easy to extract these semantic meanings into our metadata model.

Rather than modify our base datafile and make assumptions what later analysis would require, we built a utility function to convert semantic 'null' values into NaN values when desired. 

This allows us to keep the base datafile intact while still being able to perform analysis that requires NaN values.

#### Simplifying Analysis
Because the dataset used extensive mappings of numeric codes to semantic meanings, we did extend our base datafile to include human-readable `_DESC` columns that applied the textual descriptions from the codebook to the numeric values.

*Examples*

|      | Column Name      | Value                        | Data Type |
|----------|-----------------|------------------------------|-----------|
| Original | GENHLTH         | 1                            | numeric   |
| Added    | GENHLTH_DESC    | Excellent                    | string    |
| Original | DIABETE4        | 3                            | numeric   |
| Added    | DIABETE4_DESC   | Yes, but only during pregnancy | string    |

Done naively this did increase the memory footprint of dataset significantly (with naive _DESC fields the in memory dataset was 11GB), but we were able to mark those new _DESC as categorical as the vast majority of columns used a relatively small set of values. 

The PyArrow library that we used
for serializing our modified dataset supported persisting these datavalues. Using the categorical data type brought the memory footprint back down to 1.5GB, which was a significant reduction (87% reduction).


### Column Classification

#### Documented Columns
We identified 6 columns without standard metadata and handled them separately. This appears to be the result of recent policy changes from the current Administration. The data exists in the dataset but are not documented in the codebook. We did not use these columns in our analysis.

The remaining 344 columns were fully documented.

## General Exploration Data Analysis

