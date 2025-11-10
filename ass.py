Description:
Added a wrapper in the API to filter records based on application ID and document ID.
The logic now sets the dirty flag to true or false based on existing records.
If the document_type changes, the dirty flag is automatically set to true.
