def remove_overlapping_entities(ner_details):
    sorted_ner = sorted(ner_details, key=lambda x: x[OVERLAPPING_START_INDEX])
    non_overlapping_ner = []

    for entity in sorted_ner:
        overlapping = False

        for prev_entity in non_overlapping_ner:
            # Check for full containment
            if (
                entity[OVERLAPPING_START_INDEX] >= prev_entity[OVERLAPPING_START_INDEX] and
                entity[OVERLAPPING_END_INDEX] <= prev_entity[OVERLAPPING_END_INDEX]
            ):
                # Only skip if text and label are same
                if (
                    entity[ENTITY_TEXT].strip().lower() == prev_entity[ENTITY_TEXT].strip().lower() and
                    entity[LABEL].lower() == prev_entity[LABEL].lower()
                ):
                    overlapping = True
                    break  # safe to ignore

        if not overlapping:
            non_overlapping_ner.append(entity)

    return non_overlapping_ner
