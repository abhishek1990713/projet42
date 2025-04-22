import os
import cv2
import pandas as pd
from mrz_reader.reader import MRZReader

# Constants
SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".tif")
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output_folder"
OUTPUT_EXCEL = "ocr_results.xlsx"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure output folder exists

# Model paths
det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

# Initialize MRZReader
reader = MRZReader(
    facedetection_protxt="/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/face_detector/deploy.prototxt",
    facedetection_caffemodel=r"/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/face_detector/res10_300x300_ssd_iter_140000_fp16.caffemodel",
    segmentation_model=r"/home/ko19678/japan_pipeline/MRZ_Passport_Reader_From_Image-main/weights/mrz_detector/mrz_segmentation.onnx",
    use_paddle_ocr=True,
    det_model_dir=det_model_dir,
    rec_model_dir=rec_model_dir,
    cls_model_dir=cls_model_dir,
)

# Collect results
results_list = []

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(SUPPORTED_FORMATS):
        image_path = os.path.join(INPUT_FOLDER, filename)
        try:
            text_results, segmented_image, face = reader.predict(
                image_path,
                do_facedetect=True,
                preprocess_config={
                    "do_preprocess": True,
                    "skewness": True,
                    "delete_shadow": True,
                    "clear_background": True
                }
            )

            # Save segmented image
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            cv2.imwrite(output_path, segmented_image)

            # Store OCR results
            for bbox, text, confidence in text_results:
                results_list.append({
                    "Filename": filename,
                    "BoundingBox": str(bbox),
                    "Text": text,
                    "Confidence": round(confidence, 2)
                })

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            results_list.append({
                "Filename": filename,
                "BoundingBox": None,
                "Text": f"Error: {e}",
                "Confidence": None
            })

# Create or append to Excel
df_new = pd.DataFrame(results_list)

if os.path.exists(OUTPUT_EXCEL):
    df_existing = pd.read_excel(OUTPUT_EXCEL)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_excel(OUTPUT_EXCEL, index=False)
else:
    df_new.to_excel(OUTPUT_EXCEL, index=False)

print(f"OCR results written to {OUTPUT_EXCEL}")
print(f"Segmented images saved in '{OUTPUT_FOLDER}'")
