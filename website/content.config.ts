import { defineCollection, defineContentConfig, z } from '@nuxt/content'

export default defineContentConfig({
    collections: {
        docs: defineCollection({
            source: '*.md',
            type: 'page'
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
                                missing: z.boolean().optional()
                            }),
                            // ValueRange
                            z.object({
                                description: z.string(),
                                missing: z.boolean().optional(),
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
                            unique_count: z.number().nullable().optional(),
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
                            unique_count: z.number().nullable().optional(),
                            value_counts: z.record(z.string(), z.number()),
                            top_values: z.array(
                                z.object({
                                    value: z.string(),
                                    count: z.number(),
                                    description: z.string().optional()
                                })
                            )
                        })
                    ]).optional()
                }))
            })
        })
    }
})