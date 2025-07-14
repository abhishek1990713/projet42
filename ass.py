
import cv2
import xml.etree.ElementTree as ET

# === Configuration ===
xml_file = "data.xml"
image_file = "image.jpg"
output_file = "output_with_boxes.jpg"

# === Load image ===
image = cv2.imread(image_file)
if image is None:
    raise FileNotFoundError(f"Image not found: {image_file}")
img_h, img_w = image.shape[:2]
print(f"Image size: width={img_w}, height={img_h}")

# === Parse XML ===
tree = ET.parse(xml_file)
root = tree.getroot()

# Handle namespace
namespace = {'ns': root.tag.split('}')[0].strip('{')}

# Get <Fields> section
fields = root.find('ns:Fields', namespace)
if fields is None:
    raise ValueError("No <Fields> section found in the XML")

# === Draw bounding boxes ===
for field in fields.findall('ns:Field', namespace):
    try:
        label = field.find('ns:LabelName', namespace).text or ""
        value = field.find('ns:Value', namespace).text or ""

        x = int(field.find('ns:RectangleX', namespace).text)
        y = int(field.find('ns:RectangleY', namespace).text)
        w = int(field.find('ns:RectangleWidth', namespace).text)
        h = int(field.find('ns:RectangleHeight', namespace).text)

        print(f"Drawing: {label}, x={x}, y={y}, w={w}, h={h}")

        # Minimum box size for visibility
        if w < 5: w = 20
        if h < 5: h = 20

        # Draw bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Draw label text
        cv2.putText(image, f"{label}: {value}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    except Exception as e:
        print(f"Skipping one field due to error: {e}")

# === Save output ===
cv2.imwrite(output_file, image)
print(f"✅ Saved: {output_file}")
