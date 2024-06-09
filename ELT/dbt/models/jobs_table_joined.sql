SELECT *
FROM jobs_table
JOIN summarized_data_table
ON jobs.URL = summarized_data_table.source