def remove_overlapping_entities(ner_details):
    sorted_ner = sorted(
        ner_details,
        key=lambda x: (x[START_INDEX], -(x[END_INDEX] - x[START_INDEX]))
    )

    non_overlapping = []

    for current in sorted_ner:
        overlap_found = False
        for existing in non_overlapping:
            # Check for any overlap
            if not (current[END_INDEX] < existing[START_INDEX] or current[START_INDEX] > existing[END_INDEX]):
                overlap_found = True
                print(f"\n⚠️ OVERLAP FOUND:")
                print(f"  ❌ Current entity: {current[ENTITY_TEXT]} ({current[START_INDEX]}-{current[END_INDEX]})")
                print(f"  ✅ Existing entity: {existing[ENTITY_TEXT]} ({existing[START_INDEX]}-{existing[END_INDEX]})")
                break

        if not overlap_found:
            non_overlapping.append(current)
        else:
            print(f"  🔥 REMOVED: {current[ENTITY_TEXT]}")

    print(f"\n✅ Original count: {len(ner_details)}")
    print(f"✅ Remaining after removing overlaps: {len(non_overlapping)}")
    return non_overlapping
