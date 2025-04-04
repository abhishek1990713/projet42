# constant.py

# Logging Messages
LOG_PPOCR_LEVEL = 'ppocr'
LOGGING_LEVEL = 'WARNING'
LOGGER_NAME = 'passport_logger'
LOG_FILE_NAME = 'passport_app.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Paths
DOCTR_CACHE_DIR = '/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models'
PASSPORT_MODEL_PATH = '/home/ko19678/japan_pipeline/ALL_Passport/best.pt'
DET_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer'
REC_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer'
CLS_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer'

# Labels
MRL_ONE = 'MRL_One'
MRL_SECOND = 'MRL_Second'

# Error Messages
ERR_IMAGE_DECODE = 'Unable to decode image'
ERR_IMAGE_PROCESS = 'Image processing error: '
ERR_PDF_PROCESS = 'PDF processing error: '
ERR_TIFF_PROCESS = 'TIFF processing error: '
ERR_UNSUPPORTED_FORMAT = 'Unsupported file format'
ERR_PROCESSING = 'Processing error: '

# Response
STATUS_SUCCESS = 'success'
STATUS_ERROR = 'error'

# Gender Mapping
GENDER_MAPPING = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}

# Date Validation
VALID_ISSUE_DATE = '22 AUG 2010'
VALID_EXPIRY_DATE = '22 AUG 2029'
