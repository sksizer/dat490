## Tooling
Because of the breadth of data present. 

### Interactive Column Browser
- **[Comprehensive Feature Catalog](https://singular-eclair-6a5a16.netlify.app/columns)**: Browse all 344 documented columns with detailed metadata
- **[Advanced Filtering](https://singular-eclair-6a5a16.netlify.app/columns?section=Demographics)**: Filter by section, variable type, computed vs. survey questions
- **Multi-column Selection**: Select specific features for custom analysis
- **Real-time Search**: Search across column names, labels, questions, and sections

### Statistical Analysis Dashboard
- **Observation Count Visualization**: Interactive bar charts showing response counts per feature
- **Data Completeness Analysis**: Statistical breakdown of valid responses, missing data, and null values
- **Response Quality Metrics**: Mean, median, standard deviation, and quartile analysis
- **Completion Rate Distribution**: Categorized view of data quality (excellent, good, fair, poor)

### Demographic Analysis Integration
- **[Machine Learning Insights](https://singular-eclair-6a5a16.netlify.app/demographic-analysis)**: Random Forest model results showing demographic predictability
- **Feature Importance Rankings**: Identify which health factors are most predictable by demographics
- **[Accuracy Metrics](https://singular-eclair-6a5a16.netlify.app/columns/GENHLTH/demographic-analysis)**: Model performance indicators for each analyzed feature
- **Cross-sectional Analysis**: 200+ demographic prediction models across health topics


| Metric                      | Value             |
|-----------------------------|-------------------|
| Valid Responses             | 94.5%             |
| Missing/Refused             | 4.1%              |
| Null Values                 | 49.2%             |
| Semantic Nulls              | 51.1%             |
|                             |                   |
| Mean Responses per Feature  | 211,809           |
| Median Responses            | 217,736           |
| Min Responses               | 0                 |
| Max Responses               | 433,323           |
| Std Dev (Responses)         | 178,584           |
| IQR (Responses)             | 22,027–411,209    |
|                             |                   |
| Mean Completion Rate        | 94.5%             |
| Median Completion Rate      | 98.8%             |
| Completion Rate Std Dev     | 14.7%             |
| Completion Rate Range       | 0% – 100%         |
| Excellent Completion (≥95%) | 262 features      |
| Poor Completion (<60%)      | 9 features        |
|                             |                   |
| Total Features Analyzed     | 343               |
