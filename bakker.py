

from PIL import Image

def images_to_pdf(image_folder, output_pdf):
    images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.lower().endswith((".png", ".jpg", ".jpeg"))]
    images.sort()  # Sort images to maintain order

    if not images:
        print("No images found!")
        return

    # Open first image and convert it to RGB
    first_image = Image.open(images[0]).convert("RGB")
    image_list = [Image.open(img).convert("RGB") for img in images[1:]]

    # Save as a PDF
    first_image.save(output_pdf, save_all=True, append_images=image_list)
    print(f"PDF saved: {output_pdf}")

# Example Usage
image_folder = "path/to/output/images"
output_pdf = "path/to/final_output.pdf"
images_to_pdf(image_folder, output_pdf)
