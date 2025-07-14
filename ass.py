
import cv2
import xml.etree.ElementTree as ET

# Load the XML file
xml_file = 'data.xml'  # Replace with your actual XML file name
image_path = 'image.jpg'

# Parse the XML
tree = ET.parse(xml_file)
root = tree.getroot()

# Get the namespace from the root tag (if any)
namespace = {'ns': root.tag.split('}')[0].strip('{')}

# Load the image
image = cv2.imread(image_path)

# Go to the <Fields> section
fields = root.find('ns:Fields', namespace)

for field in fields.findall('ns:Field', namespace):
    label = field.find('ns:LabelName', namespace).text
    value = field.find('ns:Value', namespace).text
    x = int(field.find('ns:Rectanglex', namespace).text)
    y = int(field.find('ns:RectangleY', namespace).text)
    w = int(field.find('ns:RectangleWidth', namespace).text)
    h = int(field.find('ns:RectangleHeight', namespace).text)

    # Draw rectangle
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Add label text
    cv2.putText(image, f"{label}: {value}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 1)

# Save the result
cv2.imwrite("output_with_boxes.jpg", image)
print("Saved: output_with_boxes.jpg")
