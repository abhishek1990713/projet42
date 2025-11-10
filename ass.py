Description:
Added a wrapper in the API to filter records based on application ID and document ID.
The logic now sets the dirty flag to true or false based on existing records.
If the document_type changes, the dirty flag is automatically set to true.


Acceptance Criteria

The API must include a wrapper that filters data based on:

Application ID

Document ID

The API should check existing records and update the dirty flag as follows:

If no changes are detected → dirty = false

If changes are detected → dirty = true

If the document_type is modified compared to existing records, the system must automatically set dirty = true.

The wrapper must return only the filtered and updated records with the correct dirty status.

Proper logging and error handling should be implemented for all filter and update operations
