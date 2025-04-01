import cv2
import os
import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

def detect_skew_angle(image_path):
    """Detects the skew angle of a given image."""
    if not os.path.exists(image_path):
        print(f"X Error: File '{image_path}' not found.")
        return None

    print(f"Processing image: {image_path}")

    img = cv2.imread(image_path)

    if img is None:
        print("X Error: Unable to read the image file.")
        return None

    # Perform skew detection using AsposeOCR
    try:
        ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
        ocr_input.add(image_path)
        angles = api.calculate_skew(ocr_input)
    except RuntimeError as e:
        print(f"A Warning: Skew detection failed - {e}")
        return None

    if angles:
        skew_angle = angles[0].angle
        print(f"Skew Angle Detected = {skew_angle:.2f}")
        return skew_angle
    else:
        print("No skew detected")
        return None

def crop_and_save_image(input_image_path, output_folder):
    """Crops an image into five vertical sections and saves them."""
    # Read the input image
    image = cv2.imread(input_image_path)

    if image is None:
        raise ValueError("Image not found or unable to read the file.")

    # Get image dimensions
    height, width, _ = image.shape

    # Calculate the width of each vertical crop
    crop_width = width // 5

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Crop and save each vertical section
    for i in range(5):
        # Define the cropping region
        x_start = i * crop_width
        x_end = (i + 1) * crop_width if i < 4 else width  # Ensure the last crop includes the remaining pixels

        cropped_image = image[:, x_start:x_end]

        # Save the cropped image
        output_path = os.path.join(output_folder, f"cropped_section_{i + 1}.jpg")
        cv2.imwrite(output_path, cropped_image)

        print(f"Saved: {output_path}")

        # Detect skew angle for the cropped image
        skew_angle = detect_skew_angle(output_path)

        if skew_angle is not None:
            print(f"Skew angle for section {i + 1}: {skew_angle:.2f}°")
        else:
            print(f"No skew detected for section {i + 1}.")

if __name__ == "__main__":
    # Example: Replace with your actual image path
    image_path = r"your_image_path_here.jpg"  # Provide the path to your image
    output_folder = r"your_output_folder_here"  # Provide the folder where cropped images will be saved

    crop_and_save_image(image_path, output_folder)
