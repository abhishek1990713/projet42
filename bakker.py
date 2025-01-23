                        +-------------------------+
                        |   User Uploads File     |
                        |  (via FastAPI Endpoint) |
                        +------------+------------+
                                     |
                                     v
                        +----------------------------+
                        | FastAPI Endpoint           |
                        | (/process-file/)           |
                        +----------------------------+
                                     |
                                     v
                        +-----------------------------+
                        | Save Uploaded File          |
                        | (temp_<file.filename>)      |
                        +-----------------------------+
                                     |
                                     v
                        +-----------------------------+
                        | File Format Validation      |
                        |  (Image/PDF Classification) |
                        +-----------------------------+
                                     |
                        +------------+------------+-------------+
                        |            |            |             |
                        v            v            v             v
        +-----------------------+  +---------------------+  +-------------------+  +-------------------+
        | Image Classification   |  | PDF Classification  |  | OCR Text Extraction|  | MNC Processing    |
        | - Driving License      |  | - Extract Pages     |  | - YOLO for Corners |  | - Extract MNC     |
        | - Passport             |  | - Extract Images    |  | - PaddleOCR Text   |  | - Extract Info    |
        | - Residence Card       |  | - Process Images    |  | - Data Extraction  |  |                   |
        +-----------------------+  +---------------------+  +-------------------+  +-------------------+
                                     |
                                     v
                      +-----------------------------------+
                      | Document Type Classification     |
                      | - Driving License                |
                      | - Passport                       |
                      | - Residence Card                 |
                      | - Miscellaneous (MNC)            |
                      +-----------------------------------+
                                     |
                                     v
                +--------------------------------------------+
                | Process Relevant Document Type           |
                | (Use Specific Processing Logic per Type)  |
                +-------------------+------------------------+
                                     |
                  +------------------+--------------------+
                  |                  |                    |
                  v                  v                    v
         +---------------------+ +--------------------+ +--------------------+  +-------------------+
         | Process DL Document | | Process Passport   | | Process RC Document|  | Process MNC Document|
         | - Extract Info       | | - Extract Info      | | - Extract Info      |  | - Extract Info      |
         | - Validate Info      | | - Validate Info     | | - Validate Info     |  | - Validate Info     |
         +---------------------+ +--------------------+ +--------------------+  +-------------------+
                                     |
                                     v
                    +--------------------------------------+
                    | Validate Extracted Information      |
                    | - Check Expiry Date Validity        |
                    | - Check Validity of Data Fields     |
                    +--------------------------------------+
                                     |
                                     v
                          +-----------------------------+
                          | Return Results to User      |
                          | - JSON Response             |
                          +-----------------------------+
                                     |
                                     v
                        +-----------------------------+
                        | Delete Temporary File       |
                        | (temp_<file.filename>)      |
                        +-----------------------------+
