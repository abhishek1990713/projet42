import cv2
from paddleocr import PaddleOCR
from your_module.segmentation import SegmentationNetwork
from your_module.face_detection import FaceDetection
from your_module.utils import (
    delete_shadow, clear_background,
    determine_skew, rotate
)

class MRZReader:
    def __init__(self,
                 easy_ocr_params: dict = None,
                 use_paddle_ocr: bool = False,
                 det_model_dir: str = None,
                 rec_model_dir: str = None,
                 cls_model_dir: str = None,
                 facedetection_protxt: str = "",
                 facedetection_caffemodel: str = "",
                 segmentation_model: str = ""
                 ):
        self.segmentation = SegmentationNetwork(segmentation_model)
        self.face_detection = FaceDetection(facedetection_protxt, facedetection_caffemodel)

        self.use_paddle_ocr = use_paddle_ocr
        if use_paddle_ocr:
            self.ocr_reader = PaddleOCR(
                det_model_dir=det_model_dir,
                rec_model_dir=rec_model_dir,
                cls_model_dir=cls_model_dir,
                use_angle_cls=True,
                use_gpu=False,
                lang="en"
            )
        else:
            from your_module.easyocr_config import instantiate_from_config_easyocr
            self.ocr_reader = instantiate_from_config_easyocr(easy_ocr_params)

    def predict(self, image, do_facedetect=False, facedetect_coef=0.1, preprocess_config=None):
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image

        face = None
        segmented_image = self.segmentation.predict(img)

        if do_facedetect:
            face, _ = self.face_detection.detect(img, facedetect_coef)

        text_results = self.recognize_text(segmented_image, preprocess_config or {})
        return text_results, segmented_image, face

    def recognize_text(self, image, preprocess_config):
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image

        if preprocess_config.get("do_preprocess", False):
            img = self.preprocess_image(img, preprocess_config)

        if self.use_paddle_ocr:
            result = self.ocr_reader.ocr(img, cls=True)
            flattened_result = [
                (box, text, float(conf)) for line in result for (box, (text, conf)) in line
            ]
            return flattened_result
        else:
            return self.ocr_reader.readtext(img)

    def preprocess_image(self, img, config):
        try:
            if config.get("skewness", False):
                img = self.correct_skew(img)
            if config.get("delete_shadow", False):
                img = delete_shadow(img)
            if config.get("clear_background", False):
                img = clear_background(img)

            img = self.apply_morphological_operations(img)
            img = self.apply_threshold(img)
        except Exception as e:
            print(f"Preprocessing failed: {e}")
        return img

    def correct_skew(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            angle = determine_skew(gray)
            return rotate(img, angle, (0, 0, 0))
        except Exception as e:
            print(f"Skew correction failed: {e}")
            return img

    def apply_morphological_operations(self, img):
        # Placeholder - implement your own method
        return img

    def apply_threshold(self, img):
        # Placeholder - implement your own method
        return img


reader = MRZReader(
    use_paddle_ocr=True,
    det_model_dir="/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer",
    rec_model_dir="/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer",
    cls_model_dir="/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer",
    facedetection_protxt="/path/to/face_deploy.prototxt",
    facedetection_caffemodel="/path/to/face_model.caffemodel",
    segmentation_model="/path/to/mrz_segmentation_model.pth"
)

results, segmented, face = reader.predict(
    image="/path/to/image.jpg",
    do_facedetect=True,
    preprocess_config={
        "do_preprocess": True,
        "skewness": True,
        "delete_shadow": True,
        "clear_background": True
    }
)
