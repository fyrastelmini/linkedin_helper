SELECT jobs_table.id, job_title, company_name, location, "URL", summarized_data
FROM jobs_table
LEFT JOIN summarized_data_table
ON jobs_table."URL" = summarized_data_table.source