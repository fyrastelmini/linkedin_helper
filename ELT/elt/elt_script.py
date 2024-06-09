import psycopg2
import os
from urllib.parse import urlparse

# Get database URL from environment variables
db_url = os.getenv("DATABASE_URL")

# Parse the database URL
parsed_url = urlparse(db_url)

# Establish a connection to the database
conn = psycopg2.connect(
    dbname=parsed_url.path[1:],
    user=parsed_url.username,
    password=parsed_url.password,
    host=parsed_url.hostname,
    port=parsed_url.port
)

# Create a cursor object
cur = conn.cursor()

# Execute a SQL query to select all data from the jobs_summarized table
cur.execute("SELECT * FROM jobs_summarized;")

# Fetch all rows from the last executed SQL command
rows = cur.fetchall()

# Print all rows
for row in rows:
    print(row)

# Close the cursor and the connection
cur.close()
conn.close()