

import cv2
import xml.etree.ElementTree as ET

# Load image and get actual dimensions
image = cv2.imread("image.jpg")
img_h, img_w = image.shape[:2]
print(f"Image dimensions: width={img_w}, height={img_h}")

# Assuming original dimensions used during XML bounding box creation
original_width = 2480
original_height = 3508

# Compute scale factors
scale_x = img_w / original_width
scale_y = img_h / original_height

# Load XML and namespace
tree = ET.parse("data.xml")
root = tree.getroot()
namespace = {'ns': root.tag.split('}')[0].strip('{')}
fields = root.find('ns:Fields', namespace)

# Draw bounding boxes
for field in fields.findall('ns:Field', namespace):
    label = field.find('ns:LabelName', namespace).text
    value = field.find('ns:Value', namespace).text

    # Read and scale coordinates
    x = int(field.find('ns:RectangleX', namespace).text)
    y = int(field.find('ns:RectangleY', namespace).text)
    w = int(field.find('ns:RectangleWidth', namespace).text)
    h = int(field.find('ns:RectangleHeight', namespace).text)

    x = int(x * scale_x)
    y = int(y * scale_y)
    w = int(w * scale_x)
    h = int(h * scale_y)

    print(f"Drawing: {label}, x={x}, y={y}, w={w}, h={h}")

    # Draw box and label
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image, f"{label}: {value}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 1)

# Save result
cv2.imwrite("output_with_boxes.jpg", image)
print("✅ Output saved as output_with_boxes.jpg")
