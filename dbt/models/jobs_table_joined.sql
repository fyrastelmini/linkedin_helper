SELECT *
FROM jobs_table
JOIN summarized_data_table
ON jobs_table.URL = summarized_data_table.source