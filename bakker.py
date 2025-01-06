from flask import Flask, jsonify, request
import ssl

def preprocess_and_save_image(image_path: str, output_path: str, threshold: int = 127, thresh: int = 20) -> str:
    noise_rem_img = noise_removal(image_path, threshold, thresh)
    output_filename = os.path.splitext(os.path.basename(image_path))[0] + '_noise_removed.png'  # Ensure valid extension
    output1_path = os.path.join(output_path, output_filename)
    
    # Save the processed image and check for success
    if cv2.imwrite(output1_path, noise_rem_img):
        print(f"Processed image saved at: {output1_path}")
    else:
        raise IOError(f"Failed to save processed image to: {output1_path}")
    
    return output1_path

def check_and_preprocess(image_path: str, output_path: str) -> str:
    noise_level = calculate_noise(image_path)
    noise = noise2(image_path)

    print(f"Initial noise level: {noise_level}")
    print(f"Initial noise: {noise}")

    if (40 < noise_level < 50 and noise > 17) or (78 < noise_level < 88 and noise > 17):
        print("The scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    elif noise_level > 90:
        print("The scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    else:
        print("The scanned document image has no significant noise. No processing required.")
        return image_path

    # Check if the processed image exists before calculating noise
    if not os.path.exists(processed_image_path):
        raise FileNotFoundError(f"Processed image not found: {processed_image_path}")

    print("\nAfter preprocessing:")
    processed_noise_level = calculate_noise(processed_image_path)
    processed_noise = noise2(processed_image_path)
    print(f"Noise level after preprocessing: {processed_noise_level}")
    print(f"Noise after preprocessing: {processed_noise}")

    return processed_image_path

if __name__ == "__main__":
    image_path = r"C:\CitiDev\text_ocr\tl_classification\alldata\full_dataset\Invoice\CD_b48be2e6-5cb1-1fae-4c6c-abf38988a21c_365.png"
    output_folder = r"C:\CitiDev\output"
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        processed_image_path = check_and_preprocess(image_path, output_folder)
        print(f"Processing completed. Result saved at: {processed_image_path}")
    except Exception as e:
        print(f"Error: {e}")
