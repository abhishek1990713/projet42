
def remove_overlapping_entities(ner_details):
    # Sort: start first, then prefer longer spans
    sorted_ner = sorted(ner_details, key=lambda x: (x[START_INDEX], -(x[END_INDEX] - x[START_INDEX])))
    non_overlapping = []

    for current in sorted_ner:
        is_nested = False
        for existing in non_overlapping:
            # Check if current is fully contained in existing
            if current[START_INDEX] >= existing[START_INDEX] and current[END_INDEX] <= existing[END_INDEX]:
                is_nested = True
                print(f"❌ Removing nested entity: {current[ENTITY_TEXT]} ({current[START_INDEX]}-{current[END_INDEX]}) "
                      f"inside {existing[ENTITY_TEXT]} ({existing[START_INDEX]}-{existing[END_INDEX]})")
                break

        if not is_nested:
            non_overlapping.append(current)

    print(f"\n✅ Final count after removing nested overlaps: {len(non_overlapping)}")
    return non_overlapping
