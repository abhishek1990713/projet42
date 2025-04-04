import logging

# Logging Configuration
LOG_PPOCR_LEVEL = 'ppocr'
LOGGING_LEVEL = logging.WARNING
LOGGER_NAME = 'passport_logger'
LOG_FILE_NAME = 'passport_app.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log Messages
LOG_START_PROCESSING = "Starting passport processing."
LOG_PROCESSING_COMPLETE = "Passport processing completed."
LOG_MRL_LABEL_FOUND = "MRZ Label '{}' found."
LOG_LABEL_FOUND = "Label '{}' found."
LOG_TEXT_EXTRACTED = "Text extracted for label '{}': {}"

# Error Messages
ERROR_UNSUPPORTED_FORMAT = "Unsupported file format"
ERROR_IMAGE_PROCESSING = "Image processing error: {}"
ERROR_PDF_PROCESSING = "PDF processing error: {}"
ERROR_TIFF_PROCESSING = "TIFF processing error: {}"
ERROR_PROCESSING = "Processing error: {}"
ERROR_DECODE_IMAGE = "Unable to decode image"
ERROR_GENERAL = "An unexpected error occurred: {}"

# API Response Keys
SUCCESS_RESPONSE = "success"
ERROR_RESPONSE = "error"

# MRZ Constants
DEFAULT_MRZ_LENGTH = 44
UNKNOWN_VALUE = "Unknown"
INVALID_DATE = "Invalid Date"
N_A_VALUE = "N/A"

# PaddleOCR Configuration
USE_GPU = False
USE_ANGLE_CLS = False
USE_CLS = False
USE_DET = True
USE_REC = True
OCR_LANG = 'en'
