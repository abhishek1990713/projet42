from flask import Flask, jsonify, request
import ssl

def calculate_metrics(image_path: str) -> Tuple[float, float]:
    """Calculate noise-related metrics for an image."""
    noise_level = calculate_noise(image_path)
    noise_variance = noise2(image_path)
    return noise_level, noise_variance

def print_metrics(image_path: str, stage: str):
    """Print noise metrics for a given stage (before/after preprocessing)."""
    noise_level, noise_variance = calculate_metrics(image_path)
    print(f"\nMetrics {stage}:")
    print(f" - Noise level: {noise_level}")
    print(f" - Noise variance: {noise_variance}")

def check_and_preprocess(image_path: str, output_path: str) -> str:
    # Print initial metrics
    print_metrics(image_path, "before preprocessing")

    # Determine if preprocessing is needed
    noise_level, noise_variance = calculate_metrics(image_path)
    if (40 < noise_level < 50 and noise_variance > 17) or (78 < noise_level < 88 and noise_variance > 17):
        print("\nThe scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    elif noise_level > 90:
        print("\nThe scanned document image has significant noise. Processing recommended.")
        processed_image_path = preprocess_and_save_image(image_path, output_path)
    else:
        print("\nThe scanned document image has no significant noise. No processing required.")
        return image_path

    # Print metrics after preprocessing
    print_metrics(processed_image_path, "after preprocessing")

    return processed_image_path

if __name__ == "__main__":
    image_path = r"C:\CitiDev\Trade_doc\AWB_output_jpg\310089119_21530133_1_2303725310089119.008.jpg"
    output_folder = r"C:\CitiDev\Image_preprocessing\Output"
    os.makedirs(output_folder, exist_ok=True)
    processed_image_path = check_and_preprocess(image_path, output_folder)
    print(f"\nProcessing completed. Result saved at: {processed_image_path}")
