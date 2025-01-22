from ultralytics import YOLO  # Import YOLO library
import yaml  # Import yaml to handle the dataset.yaml file

# Load the existing model
existing_model_path = r"C:\CitiDev\Projects\YOLO_Increamental_learning\best.pt"
model = YOLO(existing_model_path)

# Print the old classes
print("Old Classes:", model.names)

# Get the old classes
old_classes = list(model.names.values())

# Define new classes to add
new_classes = ["new_class1", "new_class2", "new_class3"]  # Replace with your actual new class names

# Combine old and new classes
updated_classes = old_classes + new_classes
print("Updated Classes:", updated_classes)

# Update the model's class names
model.names = {i: name for i, name in enumerate(updated_classes)}  # Directly assign updated class names to model

# Print the updated class names
print("Updated Model Names:", model.names)

# Optionally, update the number of classes in the dataset.yaml file
dataset_yaml_path = r"C:\CitiDev\Projects\YOLO_Increamental_learning\update_yaml.yaml"

# Load and read the YAML file to update the number of classes
with open(dataset_yaml_path, "r") as f:
    yaml_data = yaml.safe_load(f)

# Update the number of classes (nc) in the YAML file
yaml_data["nc"] = len(updated_classes)  # Set the number of classes to the length of updated_classes

# Save the updated YAML file
with open(dataset_yaml_path, "w") as f:
    yaml.safe_dump(yaml_data, f)

print(f"Updated YAML file saved to {dataset_yaml_path}")

# Verify the updated YAML content
with open(dataset_yaml_path, "r") as f:
    updated_yaml_data = yaml.safe_load(f)
    print("Updated YAML content:", updated_yaml_data)

