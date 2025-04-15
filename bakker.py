def process_all_images_infolder(folder_path, output_excel_path):
    final_data = []
    desired_columns = [
        "Passport Number", "Date of Expiry", "DOB", "Nationality",
        "Date of Issue", "Last Name", "First Name", "MRZ_ONE", "MRZ_SECOND"
    ]

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            logger.info(f"Processing: {image_path}")
            result_df = process_passport_information(image_path)

            row_data = {col: "" for col in desired_columns}  # initialize with empty values

            for _, row in result_df.iterrows():
                label = row[constant.COLUMN_LABEL]
                value = row[constant.COLUMN_EXTRACTED_TEXT]

                if label == constant.LABEL_PASSPORT_NUMBER:
                    row_data["Passport Number"] = value
                elif label == constant.LABEL_EXPIRY_DATE:
                    row_data["Date of Expiry"] = value
                elif label == constant.LABEL_DATE_OF_BIRTH:
                    row_data["DOB"] = value
                elif label == constant.LABEL_NATIONALITY:
                    row_data["Nationality"] = value
                elif label == constant.LABEL_DATE_OF_ISSUE:
                    row_data["Date of Issue"] = value
                elif label == constant.LABEL_SURNAME:
                    row_data["Last Name"] = value
                elif label == constant.LABEL_GIVEN_NAMES:
                    row_data["First Name"] = value
                elif label == constant.MRZ_ONE:
                    row_data["MRZ_ONE"] = value
                elif label == constant.MRZ_SECOND:
                    row_data["MRZ_SECOND"] = value

            final_data.append(row_data)

    final_df = pd.DataFrame(final_data, columns=desired_columns)
    
    final_df.to_excel(output_excel_path, index=False)
    logger.info(f"Saved results to Excel: {output_excel_path}")
"
