

import cv2
import xml.etree.ElementTree as ET

# Load image
image = cv2.imread("image.jpg")
img_h, img_w = image.shape[:2]
print(f"Image dimensions: width={img_w}, height={img_h}")

# Original dimensions from OCR engine
original_width = 2480
original_height = 3508

# Calculate scaling factors
scale_x = img_w / original_width
scale_y = img_h / original_height

print(f"Scale X: {scale_x:.3f}, Scale Y: {scale_y:.3f}")

# Load and parse XML
tree = ET.parse("data.xml")
root = tree.getroot()
namespace = {'ns': root.tag.split('}')[0].strip('{')}
fields = root.find('ns:Fields', namespace)

# Draw bounding boxes
for field in fields.findall('ns:Field', namespace):
    label = field.find('ns:LabelName', namespace).text
    value = field.find('ns:Value', namespace).text

    # Read raw coords
    x = int(field.find('ns:RectangleX', namespace).text)
    y = int(field.find('ns:RectangleY', namespace).text)
    w = int(field.find('ns:RectangleWidth', namespace).text)
    h = int(field.find('ns:RectangleHeight', namespace).text)

    # Apply scaling
    x = int(x * scale_x)
    y = int(y * scale_y)
    w = max(20, int(w * scale_x))  # enforce minimum width
    h = max(20, int(h * scale_y))  # enforce minimum height

    print(f"Drawing: {label}, x={x}, y={y}, w={w}, h={h}")

    # Draw box
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Put text
    cv2.putText(image, f"{label}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

# Save output
cv2.imwrite("output_with_boxes.jpg", image)
print("✅ Saved: output_with_boxes.jpg")
