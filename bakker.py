from arz_reader.reader import MRZReader

def run_mrz_reader(image_path: str) -> list:
    """
    Run MRZReader to detect and recognize text from a passport image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        list: Recognized text strings.
    """
    # Define model paths
    det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
    rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
    cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

    # Initialize MRZReader
    reader = MRZReader(
        facedetection_protxt=r"/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/face_detector/deploy.prototxt",
        facedetection_caffemodel=r"/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/face_detector/res10_300x300_ssd_iter_140000.caffemodel",
        segmentation_model=r"/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/mrz_detector/mrz_seg.tflite",
        use_paddle_ocr=True,
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir
    )

    # Define preprocessing configuration
    preprocess_config = {
        "do_preprocess": True,
        "skewness": True,
        "delete_shadow": True,
        "clear_background": True
    }

    # Run prediction
    text_results, segmented_image, face = reader.predict(
        image_path,
        do_facedetect=True,
        preprocess_config=preprocess_config
    )

    # Return only the recognized text
    return [text for _, text, _ in text_results]

