SELECT job_title, company_name, location, "URL"
FROM jobs_table
LEFT JOIN summarized_data_table
ON jobs_table."URL" = summarized_data_table.source