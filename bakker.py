import re
from arz_reader.reader import MRZReader

def extract_mrz_text(image_path):
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

    # Define preprocessing options
    preprocess_config = {
        "do_preprocess": True,
        "skewness": True,
        "delete_shadow": True,
        "clear_background": True
    }

    # Run prediction
    text_results, _, _ = reader.predict(
        image_path,
        do_facedetect=True,
        preprocess_config=preprocess_config
    )

    # Initialize lists to store cleaned lines
    mrl_one = ""
    mrl_second = ""

    # Process each recognized text
    for idx, (_, text, _) in enumerate(text_results):
        cleaned = text.replace(" ", "")
        # Replace <S<, <SS<<, multiple S and K patterns with <
        cleaned = re.sub(r"<S<|<SS<<|S{2,}", "<", cleaned)
        cleaned = re.sub(r"<K<|<KK<<|K{2,}", "<", cleaned)
        
        # Split into mrl_one and mrl_second based on line index
        if idx == 0:
            mrl_one = cleaned
        elif idx == 1:
            mrl_second = cleaned

    return mrl_one, mrl_second

# Example usage:
# mrl_one, mrl_second = extract_mrz_text("/path/to/image.png")
# print("First Line:", mrl_one)
# print("Second Line:", mrl_second)
