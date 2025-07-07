def remove_overlapping_entities(ner_details):
    # Sort entities by START_INDEX, and prefer longer spans (END_INDEX - START_INDEX)
    sorted_ner = sorted(
        ner_details,
        key=lambda x: (x[START_INDEX], -(x[END_INDEX] - x[START_INDEX]))
    )

    non_overlapping = []

    for current in sorted_ner:
        overlap_found = False
        for existing in non_overlapping:
            # Only skip if there's an actual overlap
            if not (
                current[END_INDEX] < existing[START_INDEX]
                or current[START_INDEX] > existing[END_INDEX]
            ):
                overlap_found = True
                break

        if not overlap_found:
            non_overlapping.append(current)

    return non_overlapping
