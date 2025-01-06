from flask import Flask, jsonify, request
import ssl

def check_and_preprocess(image_path: str, output_path: str) -> str:
    # Initial noise calculation
    noise_level = calculate_noise(image_path)
    noise = noise2(image_path)

    print(f"Initial noise level: {noise_level}")
    print(f"Initial noise: {noise}")

    # Determine if preprocessing is needed
    if (40 < noise_level < 50 and noise > 17) or (78 < noise_level < 88 and noise > 17):
        print("The scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    elif noise_level > 90:
        print("The scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    else:
        print("The scanned document image has no significant noise. No processing required.")
        return image_path

    # Calculate noise after preprocessing
    print("\nAfter preprocessing:")
    processed_noise_level = calculate_noise(processed_image_path)
    processed_noise = noise2(processed_image_path)
    print(f"Noise level after preprocessing: {processed_noise_level}")
    print(f"Noise after preprocessing: {processed_noise}")

    return processed_image_path

if __name__ == "__main__":
    image_path = r"C:\CitiDev\Trade_doc\AWB_output_jpg\310089119_21530133_1_2303725310089119.008.jpg"
    output_folder = r"C:\CitiDev\Image_preprocessing\Output"
    os.makedirs(output_folder, exist_ok=True)
    processed_image_path = check_and_preprocess(image_path, output_folder)
    print(f"Processing completed. Result saved at: {processed_image_path}")
