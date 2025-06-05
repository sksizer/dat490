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
                    value_lookup: z.record(z.string(), z.string())
                }))
            })
        })
    }
})