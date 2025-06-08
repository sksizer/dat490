import { defineCollection, defineContentConfig, z } from '@nuxt/content'

export default defineContentConfig({
    collections: {
        docs: defineCollection({
            source: '*.md',
            type: 'page'
        }),
        demographic_analysis: defineCollection({
            source: '*_demographic_analysis.json',
            type: 'data',
            schema: z.object({
                target_column: z.string(),
                accuracy: z.number(),
                classification_report: z.record(z.string(), z.any()),
                feature_importance: z.array(z.object({
                    feature: z.string(),
                    importance: z.number()
                })),
                confusion_matrix: z.array(z.array(z.number().int())),
                class_labels: z.array(z.string()),
                model_parameters: z.record(z.string(), z.any()),
                analysis_metadata: z.record(z.string(), z.any()),
                successful: z.boolean().default(true),
                error_message: z.string().nullable().optional()
            })
        }),
        feature_importance_summary: defineCollection({
            source: 'feature_importance_summary.json',
            type: 'data',
            schema: z.object({
                total_analyses: z.number(),
                successful_analyses: z.number(),
                average_accuracy: z.number(),
                top_features: z.array(z.object({
                    feature: z.string(),
                    average_importance: z.number(),
                    frequency: z.number(),
                    rank: z.number()
                })),
                feature_frequency: z.record(z.string(), z.number()),
                accuracy_distribution: z.record(z.string(), z.number()),
                sections_analyzed: z.array(z.string()),
                sections_excluded: z.array(z.string()),
                analysis_metadata: z.record(z.string(), z.any())
            })
        }),
        columns: defineCollection({
            // Load every file inside the `content` directory
            source: 'model.json',
            type: 'data',
            // Specify the type of content in this collection
            schema: z.object({
                columns: z.record(z.string(), z.object({
                    computed: z.boolean(),
                    label: z.string(),
                    sas_variable_name: z.string(),
                    section_name: z.string().nullable().optional(),
                    section_number: z.number().nullable().optional(),
                    module_number: z.number().nullable().optional(),
                    question_number: z.number().nullable().optional(),
                    column: z.string().nullable().optional(),
                    type_of_variable: z.string().nullable().optional(),
                    question_prologue: z.string().nullable().optional(),
                    question: z.string().nullable().optional(),
                    value_ranges: z.array(
                        z.union([
                            // ValueDef
                            z.object({
                                description: z.string(),
                                indicates_missing: z.boolean().optional()
                            }),
                            // ValueRange
                            z.object({
                                description: z.string(),
                                indicates_missing: z.boolean().optional(),
                                start: z.number(),
                                end: z.number(),
                                count: z.number()
                            })
                        ])
                    ),
                    value_lookup: z.record(
                        z.union([z.null(), z.number()]),
                        z.string()
                    ),
                    html_name: z.string(),
                    // Add statistics schema
                    statistics: z.union([
                        // NumericStatistics
                        z.object({
                            count: z.number(),
                            null_count: z.number(),
                            missing_count: z.number(),
                            unique_count: z.number().nullable().optional(),
                            total_responses: z.number(),
                            mean: z.number().nullable().optional(),
                            std: z.number().nullable().optional(),
                            min: z.number().nullable().optional(),
                            q25: z.number().nullable().optional(),
                            median: z.number().nullable().optional(),
                            q75: z.number().nullable().optional(),
                            max: z.number().nullable().optional()
                        }),
                        // CategoricalStatistics
                        z.object({
                            count: z.number(),
                            null_count: z.number(),
                            missing_count: z.number(),
                            unique_count: z.number().nullable().optional(),
                            total_responses: z.number(),
                            value_counts: z.record(z.string(), z.number()),
                            top_values: z.array(
                                z.object({
                                    value: z.string(),
                                    count: z.number(),
                                    description: z.string().optional(),
                                    is_missing: z.boolean().optional()
                                })
                            )
                        })
                    ]).optional(),
                    demographic_analysis_score: z.number().nullable().optional()
                }))
            })
        })
    }
})