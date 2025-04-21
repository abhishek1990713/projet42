def recognize_text(self, image, preprocess_config):
    if isinstance(image, str):
        img = cv2.imread(image, cv2.IMREAD_COLOR)
    else:
        img = image

    if preprocess_config.get("do_preprocess", False):
        img = self.preprocess_image(img, preprocess_config)

    if self.use_paddle_ocr:
        # Make sure image is in the correct format (numpy array or image path)
        result = self.ocr_reader.ocr(img, cls=True)
        # Flatten result to a consistent structure
        flattened_result = [
            (box, text, float(conf)) for line in result for (box, (text, conf)) in line
        ]
        return flattened_result
    else:
        return self.ocr_reader.readtext(img)

