

# === Logger ===
LOG_FILE_NAME = "app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGER_NAME = "passport_logger"

# === Log Messages ===
LOG_START_PROCESSING = "Started processing the passport image."
LOG_PROCESSING_COMPLETE = "Completed processing the passport image."
LOG_MRL_LABEL_FOUND = "MRZ Line Detected: {}"
LOG_LABEL_FOUND = "Non-MRZ Text Detected: {}"
LOG_TEXT_EXTRACTED = "Text extracted from {}: {}"

# === Error Messages ===
ERROR_UNSUPPORTED_FORMAT = "Unsupported file format"
ERROR_IMAGE_PROCESSING = "Image processing error: {}"
ERROR_PDF_PROCESSING = "PDF processing error: {}"
ERROR_TIFF_PROCESSING = "TIFF processing error: {}"
ERROR_PROCESSING = "Passport processing error: {}"
ERROR_DECODE_IMAGE = "Unable to decode image"

# === API Response Status ===
SUCCESS_RESPONSE = "success"
ERROR_RESPONSE = "error"

# === Placeholder Values ===
UNKNOWN_VALUE = "UNKNOWN"
N_A_VALUE = "N/A"
DEFAULT_MRZ_LENGTH = 44
