"""
Demographic Analysis Module
=========================

Reusable Random Forest analysis function for predicting BRFSS variables from demographic features.
Based on the GENHLTH demographic analysis notebook.
"""

import os
import time
import logging
import warnings
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
from pydantic import BaseModel

# Suppress sklearn warnings
warnings.filterwarnings('ignore')

# Demographic feature columns (26 total features)
DEMOGRAPHIC_FEATURE_COLUMNS = [
    # Demographics section columns (13 total)
    'MARITAL', 'EDUCA', 'RENTHOM1', 'NUMHHOL4', 'NUMPHON4', 'CPDEMO1C', 
    'VETERAN3', 'EMPLOY1', 'CHILDREN', 'INCOME3', 'PREGNANT', 'WEIGHT2', 'HEIGHT3',
    
    # Calculated demographic variables (13 total) 
    '_IMPRACE', '_CRACE1', '_MRACE1', '_RACE', '_RACEG21', '_RACEGR3', '_RACEPRV', 
    '_SEX', '_AGEG5YR', '_AGE65YR', '_AGE80', '_AGE_G', '_EDUCAG'
]


class DemographicAnalysisResult(BaseModel):
    """Result of demographic analysis for a single target column."""
    target_column: str
    accuracy: float
    classification_report: Dict[str, Any]
    feature_importance: List[Dict[str, Union[str, float]]]
    confusion_matrix: List[List[int]]
    class_labels: List[str]
    model_parameters: Dict[str, Any]
    analysis_metadata: Dict[str, Any]
    successful: bool = True
    error_message: Optional[str] = None


class FeatureImportanceSummary(BaseModel):
    """Aggregated feature importance summary across all demographic analyses."""
    total_analyses: int
    successful_analyses: int
    average_accuracy: float
    top_features: List[Dict[str, Union[str, float]]]  # Ranked by average importance
    feature_frequency: Dict[str, int]  # How often each feature appears in top 5
    accuracy_distribution: Dict[str, int]  # Accuracy ranges and counts
    sections_analyzed: List[str]
    sections_excluded: List[str]
    analysis_metadata: Dict[str, Any]  # Generation timestamp, processing time, etc.


def perform_demographic_analysis(
    df: pd.DataFrame,
    metadata: Dict[str, Any],
    target_column: str,
    feature_columns: Optional[List[str]] = None,
    min_samples: int = 1000,
    test_size: float = 0.2,
    random_state: int = 42,
    hyperparameter_tuning: bool = True,
    logger: Optional[logging.Logger] = None
) -> DemographicAnalysisResult:
    """
    Perform Random Forest demographic analysis for a target variable.
    
    Args:
        df: DataFrame with BRFSS data (semantic nulls should already be converted)
        metadata: Dictionary of column metadata 
        target_column: Name of the target variable to predict
        feature_columns: List of demographic feature columns (defaults to DEMOGRAPHIC_FEATURE_COLUMNS)
        min_samples: Minimum number of valid samples required for analysis
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        hyperparameter_tuning: Whether to perform hyperparameter tuning
        logger: Logger instance for progress tracking
        
    Returns:
        DemographicAnalysisResult containing analysis results
    """
    start_time = time.time()
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    if feature_columns is None:
        feature_columns = DEMOGRAPHIC_FEATURE_COLUMNS.copy()
    
    try:
        # Validate target column exists
        if target_column not in df.columns:
            return DemographicAnalysisResult(
                target_column=target_column,
                accuracy=0.0,
                classification_report={},
                feature_importance=[],
                confusion_matrix=[],
                class_labels=[],
                model_parameters={},
                analysis_metadata={},
                successful=False,
                error_message=f"Target column '{target_column}' not found in DataFrame"
            )
        
        # Remove target column from features if present
        available_features = [col for col in feature_columns 
                            if col in df.columns and col != target_column]
        
        if len(available_features) == 0:
            return DemographicAnalysisResult(
                target_column=target_column,
                accuracy=0.0,
                classification_report={},
                feature_importance=[],
                confusion_matrix=[],
                class_labels=[],
                model_parameters={},
                analysis_metadata={},
                successful=False,
                error_message="No valid feature columns found for analysis"
            )
        
        logger.info(f"Starting demographic analysis for {target_column}")
        logger.info(f"Using {len(available_features)} demographic features")
        
        # Create analysis dataset
        analysis_cols = [target_column] + available_features
        analysis_df = df[analysis_cols].copy()
        
        # Remove rows with missing target values
        initial_size = len(analysis_df)
        model_df = analysis_df.dropna(subset=[target_column]).copy()
        dropped_target = initial_size - len(model_df)
        
        logger.info(f"Dropped {dropped_target:,} rows with missing target values")
        
        # Check minimum sample requirement
        if len(model_df) < min_samples:
            return DemographicAnalysisResult(
                target_column=target_column,
                accuracy=0.0,
                classification_report={},
                feature_importance=[],
                confusion_matrix=[],
                class_labels=[],
                model_parameters={},
                analysis_metadata={},
                successful=False,
                error_message=f"Insufficient samples: {len(model_df)} < {min_samples} required"
            )
        
        # Handle missing values in features (drop columns >30% missing, fill remainder with mode)
        missing_threshold = 0.3
        cols_to_keep = []
        
        for col in available_features:
            missing_pct = model_df[col].isnull().sum() / len(model_df)
            
            if missing_pct <= missing_threshold:
                cols_to_keep.append(col)
            else:
                logger.info(f"Dropping {col} due to {missing_pct:.1%} missing values")
        
        feature_cols = cols_to_keep
        
        if len(feature_cols) == 0:
            return DemographicAnalysisResult(
                target_column=target_column,
                accuracy=0.0,
                classification_report={},
                feature_importance=[],
                confusion_matrix=[],
                class_labels=[],
                model_parameters={},
                analysis_metadata={},
                successful=False,
                error_message="All feature columns exceeded missing value threshold"
            )
        
        # Fill remaining missing values with mode
        for col in feature_cols:
            if model_df[col].isnull().any():
                mode_value = model_df[col].mode().iloc[0] if not model_df[col].mode().empty else 0
                filled_count = model_df[col].isnull().sum()
                model_df[col] = model_df[col].fillna(mode_value)
                logger.debug(f"Filled {filled_count:,} missing values in {col} with mode: {mode_value}")
        
        # Prepare features and target
        X = model_df[feature_cols].copy()
        y = model_df[target_column].copy()
        
        # Convert to numeric if needed
        for col in X.columns:
            if X[col].dtype == 'object':
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
            else:
                X[col] = pd.to_numeric(X[col], errors='coerce')
        
        # Ensure target is numeric
        if y.dtype == 'object':
            le_target = LabelEncoder()
            y = le_target.fit_transform(y.astype(str))
        else:
            y = pd.to_numeric(y, errors='coerce')
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(f"Training set: {X_train.shape[0]:,} samples")
        logger.info(f"Test set: {X_test.shape[0]:,} samples")
        
        # Train model
        if hyperparameter_tuning:
            logger.info("Performing hyperparameter tuning...")
            
            # Use smaller sample for grid search to speed up computation
            sample_size = min(50000, len(X_train))
            X_sample = X_train.sample(n=sample_size, random_state=random_state)
            y_sample = y_train[X_sample.index]
            
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [5, 10, 20],
                'min_samples_leaf': [2, 5, 10]
            }
            
            grid_search = GridSearchCV(
                RandomForestClassifier(random_state=random_state, n_jobs=-1),
                param_grid,
                cv=3,
                scoring='accuracy',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X_sample, y_sample)
            best_params = grid_search.best_params_
            logger.info(f"Best parameters: {best_params}")
            
            # Train final model with best parameters
            rf_model = grid_search.best_estimator_
            rf_model.fit(X_train, y_train)
        else:
            # Use default parameters
            best_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 10,
                'min_samples_leaf': 5,
                'random_state': random_state,
                'n_jobs': -1
            }
            
            rf_model = RandomForestClassifier(**best_params)
            rf_model.fit(X_train, y_train)
        
        # Make predictions and evaluate
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.3f}")
        
        # Generate classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # Generate confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Feature importance
        feature_importance_list = [
            {
                'feature': feature,
                'importance': float(importance)
            }
            for feature, importance in zip(feature_cols, rf_model.feature_importances_)
        ]
        feature_importance_list.sort(key=lambda x: x['importance'], reverse=True)
        
        # Class labels
        unique_classes = sorted(np.unique(np.concatenate([y_test, y_pred])))
        
        # Get class labels from metadata if available
        target_meta = metadata.get(target_column)
        if target_meta and hasattr(target_meta, 'value_lookup'):
            class_labels = []
            for class_val in unique_classes:
                description = target_meta.value_lookup.get(int(class_val), f"Code {class_val}")
                class_labels.append(description)
        else:
            class_labels = [f"Class {int(class_val)}" for class_val in unique_classes]
        
        # Analysis metadata
        target_dist = pd.Series(y).value_counts().sort_index()
        analysis_metadata = {
            'total_samples': int(len(model_df)),
            'training_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'features_used': feature_cols,
            'features_dropped_missing': int(len(available_features) - len(feature_cols)),
            'target_missing_dropped': int(dropped_target),
            'hyperparameter_tuning': hyperparameter_tuning,
            'analysis_time_seconds': float(time.time() - start_time),
            'target_distribution': {str(k): int(v) for k, v in target_dist.items()}
        }
        
        return DemographicAnalysisResult(
            target_column=target_column,
            accuracy=float(accuracy),
            classification_report=class_report,
            feature_importance=feature_importance_list,
            confusion_matrix=cm.tolist(),
            class_labels=class_labels,
            model_parameters=best_params,
            analysis_metadata=analysis_metadata,
            successful=True
        )
        
    except Exception as e:
        logger.error(f"Error during demographic analysis for {target_column}: {str(e)}")
        return DemographicAnalysisResult(
            target_column=target_column,
            accuracy=0.0,
            classification_report={},
            feature_importance=[],
            confusion_matrix=[],
            class_labels=[],
            model_parameters={},
            analysis_metadata={},
            successful=False,
            error_message=str(e)
        )


def generate_analysis_visualizations(
    result: DemographicAnalysisResult,
    output_dir: Path,
    format: str = 'svg'
) -> Dict[str, str]:
    """
    Generate SVG visualizations for the analysis results.
    
    Args:
        result: DemographicAnalysisResult object
        output_dir: Directory to save visualizations
        format: Image format ('svg', 'png', 'jpg')
        
    Returns:
        Dictionary mapping visualization type to file path
    """
    if not result.successful:
        return {}
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_files = {}
    
    # Confusion Matrix
    try:
        plt.figure(figsize=(8, 6))
        cm = np.array(result.confusion_matrix)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=result.class_labels,
                    yticklabels=result.class_labels)
        
        plt.title(f'Demographic Analysis: {result.target_column}\\nAccuracy: {result.accuracy:.3f}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        cm_file = output_dir / f"{result.target_column}_demographic_analysis_confusion_matrix.{format}"
        plt.savefig(cm_file, format=format, dpi=300, bbox_inches='tight')
        plt.close()
        
        generated_files['confusion_matrix'] = str(cm_file)
        
    except Exception as e:
        logging.error(f"Error generating confusion matrix for {result.target_column}: {e}")
    
    # Feature Importance - Show all features
    try:
        # Calculate figure height based on number of features
        num_features = len(result.feature_importance)
        fig_height = max(8, num_features * 0.3)  # Minimum 8 inches, 0.3 inches per feature
        
        plt.figure(figsize=(10, fig_height))
        
        # Use all features
        features = [f['feature'] for f in result.feature_importance]
        importances = [f['importance'] for f in result.feature_importance]
        
        plt.barh(range(len(features)), importances)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title(f'Feature Importance: {result.target_column}\\nAll Demographic Predictors ({num_features} features)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        fi_file = output_dir / f"{result.target_column}_demographic_analysis_feature_importance.{format}"
        plt.savefig(fi_file, format=format, dpi=300, bbox_inches='tight')
        plt.close()
        
        generated_files['feature_importance'] = str(fi_file)
        
    except Exception as e:
        logging.error(f"Error generating feature importance plot for {result.target_column}: {e}")
    
    return generated_files


def generate_feature_importance_summary(
    analysis_results: Dict[str, float],
    analysis_files_dir: Path,
    metadata: Dict[str, Any],
    excluded_sections: List[str]
) -> FeatureImportanceSummary:
    """
    Generate aggregated feature importance summary across all successful analyses.
    
    Args:
        analysis_results: Dictionary mapping column names to accuracy scores
        analysis_files_dir: Directory containing individual analysis JSON files
        metadata: Column metadata dictionary
        excluded_sections: List of sections that were excluded from target analysis
        
    Returns:
        FeatureImportanceSummary object with aggregated insights
    """
    start_time = time.time()
    
    # Collect feature importance data from all successful analyses
    feature_importance_data = []
    accuracy_scores = []
    sections_analyzed = set()
    
    for column_name, accuracy in analysis_results.items():
        analysis_file = analysis_files_dir / f"{column_name}_demographic_analysis.json"
        
        if analysis_file.exists():
            try:
                with open(analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                
                if analysis_data.get('successful', False):
                    feature_importance_data.append({
                        'column': column_name,
                        'accuracy': accuracy,
                        'features': analysis_data.get('feature_importance', [])
                    })
                    accuracy_scores.append(accuracy)
                    
                    # Track section analyzed
                    if column_name in metadata and metadata[column_name].section_name:
                        sections_analyzed.add(metadata[column_name].section_name)
                        
            except Exception as e:
                logging.warning(f"Error reading analysis file for {column_name}: {e}")
    
    # Aggregate feature importance across all analyses
    feature_totals = {}  # feature_name -> {'importance_sum': float, 'count': int, 'top5_count': int}
    
    for analysis in feature_importance_data:
        features = analysis['features']
        # Sort features by importance for this analysis
        sorted_features = sorted(features, key=lambda x: x['importance'], reverse=True)
        
        for i, feature_data in enumerate(sorted_features):
            feature_name = feature_data['feature']
            importance = feature_data['importance']
            
            if feature_name not in feature_totals:
                feature_totals[feature_name] = {
                    'importance_sum': 0.0,
                    'count': 0,
                    'top5_count': 0
                }
            
            feature_totals[feature_name]['importance_sum'] += importance
            feature_totals[feature_name]['count'] += 1
            
            # Track if this feature is in top 5 for this analysis
            if i < 5:
                feature_totals[feature_name]['top5_count'] += 1
    
    # Calculate average importance and create ranked list
    top_features = []
    for feature_name, data in feature_totals.items():
        avg_importance = data['importance_sum'] / data['count']
        frequency = data['top5_count']
        
        top_features.append({
            'feature': feature_name,
            'average_importance': avg_importance,
            'frequency': frequency,
            'rank': 0  # Will be set after sorting
        })
    
    # Sort by average importance and assign ranks
    top_features.sort(key=lambda x: x['average_importance'], reverse=True)
    for i, feature in enumerate(top_features):
        feature['rank'] = i + 1
    
    # Create feature frequency mapping
    feature_frequency = {
        feature['feature']: feature['frequency'] 
        for feature in top_features
    }
    
    # Create accuracy distribution (binned)
    accuracy_distribution = {}
    if accuracy_scores:
        import numpy as np
        
        # Create bins for accuracy distribution
        bins = np.arange(0.0, 1.1, 0.1)  # 0-10%, 10-20%, etc.
        bin_labels = [f"{int(b*100)}-{int((b+0.1)*100)}%" for b in bins[:-1]]
        
        hist, _ = np.histogram(accuracy_scores, bins=bins)
        
        for label, count in zip(bin_labels, hist):
            accuracy_distribution[label] = int(count)
    
    # Create summary object
    summary = FeatureImportanceSummary(
        total_analyses=len(analysis_results),
        successful_analyses=len(feature_importance_data),
        average_accuracy=float(np.mean(accuracy_scores)) if accuracy_scores else 0.0,
        top_features=top_features,
        feature_frequency=feature_frequency,
        accuracy_distribution=accuracy_distribution,
        sections_analyzed=sorted(list(sections_analyzed)),
        sections_excluded=excluded_sections,
        analysis_metadata={
            'generation_timestamp': time.time(),
            'processing_time_seconds': time.time() - start_time,
            'total_analyses_attempted': len(analysis_results),
            'demographic_features_used': len(DEMOGRAPHIC_FEATURE_COLUMNS)
        }
    )
    
    return summary


def generate_summary_visualizations(
    summary: FeatureImportanceSummary,
    output_dir: Path,
    format: str = 'svg'
) -> Dict[str, str]:
    """
    Generate summary visualizations for aggregated feature importance data.
    
    Args:
        summary: FeatureImportanceSummary object
        output_dir: Directory to save visualizations
        format: Image format ('svg', 'png', 'jpg')
        
    Returns:
        Dictionary mapping visualization type to file path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_files = {}
    
    # Top Features Ranking Chart
    try:
        plt.figure(figsize=(12, 8))
        
        # Show top 15 features
        top_15_features = summary.top_features[:15]
        features = [f['feature'] for f in top_15_features]
        importances = [f['average_importance'] for f in top_15_features]
        frequencies = [f['frequency'] for f in top_15_features]
        
        # Create horizontal bar chart
        y_pos = np.arange(len(features))
        bars = plt.barh(y_pos, importances, alpha=0.8)
        
        # Color bars based on frequency (how often in top 5)
        max_freq = max(frequencies) if frequencies else 1
        for bar, freq in zip(bars, frequencies):
            # Color intensity based on frequency
            color_intensity = freq / max_freq
            bar.set_color(plt.cm.Blues(0.3 + 0.7 * color_intensity))
        
        plt.yticks(y_pos, features)
        plt.xlabel('Average Feature Importance')
        plt.title(f'Top Demographic Predictors Across {summary.successful_analyses} Analyses\n' +
                 f'(Color intensity = frequency in top 5 features)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        ranking_file = output_dir / f"feature_importance_ranking.{format}"
        plt.savefig(ranking_file, format=format, dpi=300, bbox_inches='tight')
        plt.close()
        
        generated_files['ranking'] = str(ranking_file)
        
    except Exception as e:
        logging.error(f"Error generating feature importance ranking chart: {e}")
    
    # Accuracy Distribution Chart
    try:
        plt.figure(figsize=(10, 6))
        
        bins = list(summary.accuracy_distribution.keys())
        counts = list(summary.accuracy_distribution.values())
        
        if bins and counts:
            plt.bar(bins, counts, alpha=0.7, color='steelblue')
            plt.xlabel('Accuracy Range')
            plt.ylabel('Number of Analyses')
            plt.title(f'Demographic Analysis Accuracy Distribution\n' +
                     f'({summary.successful_analyses} analyses, avg: {summary.average_accuracy:.3f})')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            distribution_file = output_dir / f"analysis_accuracy_distribution.{format}"
            plt.savefig(distribution_file, format=format, dpi=300, bbox_inches='tight')
            plt.close()
            
            generated_files['distribution'] = str(distribution_file)
        
    except Exception as e:
        logging.error(f"Error generating accuracy distribution chart: {e}")
    
    return generated_files


if __name__ == "__main__":
    # Example usage
    from dat490 import load_bfrss_components
    
    # Load data
    df, metadata, logger = load_bfrss_components(semantically_null=True)
    
    # Test with GENHLTH
    result = perform_demographic_analysis(
        df=df,
        metadata=metadata,
        target_column='GENHLTH',
        logger=logger
    )
    
    print(f"Analysis successful: {result.successful}")
    if result.successful:
        print(f"Accuracy: {result.accuracy:.3f}")
        print(f"Top 3 features:")
        for i, feat in enumerate(result.feature_importance[:3], 1):
            print(f"  {i}. {feat['feature']}: {feat['importance']:.3f}")
    else:
        print(f"Error: {result.error_message}")