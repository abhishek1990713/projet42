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

    # Process each recognized text
    cleaned_texts = []
    for _, text, _ in text_results:
        cleaned = text.replace(" ", "")
        # Replace <S<, <SS<<, multiple S and K patterns with <
        cleaned = re.sub(r"<S<|<SS<<|S{2,}", "<", cleaned)
        cleaned = re.sub(r"<K<|<KK<<|K{2,}", "<", cleaned)
        cleaned_texts.append(cleaned)

    # Join all cleaned texts into a single string
    full_mrz = ''.join(cleaned_texts)

    # Split at the comma (if you want the MRZ part before and after the comma)
    if ',' in full_mrz:
        mrl_one, mrl_second = full_mrz.split(',', 1)
    else:
        # If no comma is found, return the whole MRZ text as mrl_one
        mrl_one = full_mrz
        mrl_second = ""

    return mrl_one, mrl_second

# Example usage:
# mrl_one, mrl_second = extract_mrz_text("/path/to/image.png")
# print(f"MRZ Part 1: {mrl_one}")
# print(f"MRZ Part 2: {mrl_second}")

