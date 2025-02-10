classification_result = predict_image_class(model_path, image_path)

if classification_result:
    table_data.append(["Classification", classification_result])
    logger.info(f"Predicted Class: {classification_result}")

    if classification_result == 'Driving License':
        process_result = process_dl_image(image_path)
        if process_result == 'Image is not good.':
            table_data.append(["Result", "Image is not good."])  # Add it to the table
        else:
            details = process_dl_information(image_path)
            format_df_details(table_data, details, "Driving License")

    elif classification_result == 'Passport':
        process_result = process_passport_image(image_path)
        if process_result == 'Image is not good.':
            table_data.append(["Result", "Image is not good."])  # Add it to the table
        else:
            details = process_passport_information(image_path)
            format_df_details(table_data, details, "Passport")

    elif classification_result == 'Residence Card':
        process_result = process_residence_card_image(image_path)
        if process_result == 'Image is not good.':
            table_data.append(["Result", "Image is not good."])  # Add it to the table
        else:
            details = process_residence_card_information(image_path)
            format_df_details(table_data, details, "Residence Card")

