document_stats.py

This module calculates document-level accuracy statistics for a specific 
application_id within a given date range (start_date and end_date).

📘 Description:
----------------
The function `document_stats()` retrieves feedback records for a given 
application_id and date range. For each document, it calculates the 
document-wise accuracy percentage based on field-level thumbs-up and thumbs-down 
feedback.

✅ Formula (in words):
----------------------
For each document:
    Document Accuracy (%) = (Total Thumbs-Up Fields / Total Feedback Fields) × 100

The function then counts how many documents fall into each accuracy range:
- Greater than 81%
- Between 71% and 80%
- Between 50% and 70%
- Less than 50%

Finally, it returns a structured summary showing:
- Application ID
Finally, it returns a structured summary showing:
- Application ID
- Date range used
- Total number of documents
- Count of documents in each accuracy range
""


"""
feedback_report.py

This module generates a feedback accuracy report for a specific `application_id` 
within a given date range (start_date and end_date).

📘 Description:
----------------
The function `feedback_report()` fetches all feedback entries from the database 
for a specific application and calculates field-level accuracy.

Each feedback record contains multiple fields, each having a `status` 
(either "thumbs_up" or "thumbs_down").

✅ Formula (explained in words):
--------------------------------
Field-Level Accuracy (%) = (Number of Thumbs-Up for the field / Total Feedback Count for the field) × 100

Example:
If for the field "Address", there are 8 thumbs_up and 2 thumbs_down,
then accuracy = (8 / 10) × 100 = 80%.

The function finally returns a structured response containing:
- Application ID
- Each field name
- Field-Level Accuracy (%)
- Field-Level Document Count
"""
