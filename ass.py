import json
ibXxkswMpC9a69ABUzPczmkF31toDFNLINM2JTtF
def update_dirty_status(feedback_section, existing_feedback):
    """
    Deeply compares feedback_section with existing_feedback.
    Adds or updates 'dirty' flag for every dict containing 'value'.
    Works for nested dicts and lists.
    """
    if isinstance(feedback_section, dict):
        for key, value in feedback_section.items():
            existing_value = None
            if isinstance(existing_feedback, dict):
                existing_value = existing_feedback.get(key)

            # 🔁 Recursive check for nested dict
            if isinstance(value, dict):
                # If it has a "value" key → direct compare
                if "value" in value:
                    if (
                        isinstance(existing_value, dict)
                        and "value" in existing_value
                        and existing_value["value"] == value["value"]
                    ):
                        value["dirty"] = False
                    else:
                        value["dirty"] = True
                else:
                    # Recurse deeper
                    update_dirty_status(value, existing_value if isinstance(existing_value, dict) else {})
            
            # 🔁 Handle nested lists
            elif isinstance(value, list):
                if isinstance(existing_value, list):
                    for i, item in enumerate(value):
                        if i < len(existing_value):
                            update_dirty_status(item, existing_value[i])
                        else:
                            # New list item → mark all values inside as dirty
                            mark_all_dirty(item)
                else:
                    # Entire list is new
                    for item in value:
                        mark_all_dirty(item)
            
            # ⚠️ Non-dict, non-list types → skip
            else:
                continue

    elif isinstance(feedback_section, list):
        for i, item in enumerate(feedback_section):
            existing_item = existing_feedback[i] if (
                isinstance(existing_feedback, list) and i < len(existing_feedback)
            ) else {}
            update_dirty_status(item, existing_item)


def mark_all_dirty(item):
    """Recursively mark all dicts containing 'value' as dirty."""
    if isinstance(item, dict):
        if "value" in item:
            item["dirty"] = True
        for v in item.values():
            mark_all_dirty(v)
    elif isinstance(item, list):
        for i in item:
            mark_all_dirty(i)


# ---------- MAIN LOGIC ----------
existing_feedback = {}

if existing_records:
    feedback_response = existing_records[0].feedback_response

    if isinstance(feedback_response, str):
        existing_feedback = json.loads(feedback_response).get("field_feedback", {})
    elif isinstance(feedback_response, dict):
        existing_feedback = feedback_response.get("field_feedback", {})

update_dirty_status(feedback_section, existing_feedback)

print(json.dumps(feedback_section, indent=4, ensure_ascii=False))

{
  "document_id": "DOC1234",
  "rule_id": "date_check_bm_fincen_ao_gssp",
  "status": "thumbs_up",
  "message": "Validation data processed successfully",
  "field_feedback": {
    "date_check_bm_fincen_ao_gssp": {
      "comment": "### Rule: ...",
      "status": "thumbs_up"
    }
  }
}
