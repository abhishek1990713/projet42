Hi Nikith,

That error indicates that the file_id column does not exist in the idp_feedback table. The reason is that we recently changed the column name from file_id to file_name. If you replace file_id with file_name, the error should be resolved
