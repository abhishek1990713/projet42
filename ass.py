import json

def update_dirty_status(feedback_section, existing_feedback):
    """
    Recursively update the 'dirty' status in feedback_section
    based on existing_feedback.
    Handles nested dicts and lists safely.
    """
    if isinstance(feedback_section, dict):
        for key, value in feedback_section.items():
            existing_value = existing_feedback.get(key) if isinstance(existing_feedback, dict) else None

            if isinstance(value, dict) and isinstance(existing_value, dict):
                # Recurse for nested dicts
                update_dirty_status(value, existing_value)

            elif isinstance(value, list) and isinstance(existing_value, list):
                # Recurse for lists
                for i in range(len(value)):
                    if i < len(existing_value):
                        update_dirty_status(value[i], existing_value[i])
                    else:
                        # New element not in existing feedback
                        if isinstance(value[i], dict):
                            value[i]["dirty"] = True

            else:
                # Compare leaf nodes safely
                if (
                    isinstance(value, dict)
                    and isinstance(existing_value, dict)
                    and "value" in value
                    and "value" in existing_value
                ):
                    if value["value"] == existing_value["value"]:
                        value["dirty"] = False
                    else:
                        value["dirty"] = True
                else:
                    # If not dicts (like strings, ints), cannot assign dirty
                    pass

    elif isinstance(feedback_section, list):
        for i in range(len(feedback_section)):
            if i < len(existing_feedback):
                update_dirty_status(feedback_section[i], existing_feedback[i])
            else:
                if isinstance(feedback_section[i], dict):
                    feedback_section[i]["dirty"] = True

    # Optional: return updated structure for debugging
    return feedback_section


# ---------- MAIN LOGIC ----------

existing_feedback = {}

if existing_records:
    feedback_response = existing_records[0].feedback_response

    if isinstance(feedback_response, str):
        existing_feedback = json.loads(feedback_response).get("field_feedback", {})
    elif isinstance(feedback_response, dict):
        existing_feedback = feedback_response.get("field_feedback", {})

# Recursively update dirty status for nested data
feedback_section = update_dirty_status(feedback_section, existing_feedback)
print(feedback_section)

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
