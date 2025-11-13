import json

def update_dirty_status(feedback_section, existing_feedback):
    """
    Recursively update the 'dirty' status in feedback_section
    based on the existing_feedback structure.
    Handles nested dictionaries and lists (arrays).
    """
    if isinstance(feedback_section, dict):
        for key, value in feedback_section.items():
            existing_value = existing_feedback.get(key) if isinstance(existing_feedback, dict) else None

            if isinstance(value, dict) and isinstance(existing_value, dict):
                # Recursively check nested dicts
                update_dirty_status(value, existing_value)
            elif isinstance(value, list) and isinstance(existing_value, list):
                # Recursively handle list elements
                for i in range(len(value)):
                    if i < len(existing_value):
                        update_dirty_status(value[i], existing_value[i])
                    else:
                        # New item not in existing feedback
                        if isinstance(value[i], dict):
                            value[i]["dirty"] = True
            else:
                # Compare leaf values
                if (
                    existing_value
                    and isinstance(existing_value, dict)
                    and "value" in existing_value
                    and "value" in value
                    and existing_value["value"] == value["value"]
                ):
                    value["dirty"] = False
                else:
                    value["dirty"] = True

    elif isinstance(feedback_section, list):
        # Handle top-level list
        for i in range(len(feedback_section)):
            if i < len(existing_feedback):
                update_dirty_status(feedback_section[i], existing_feedback[i])
            else:
                # New item in the list
                if isinstance(feedback_section[i], dict):
                    feedback_section[i]["dirty"] = True


# ---------- MAIN LOGIC ----------

existing_feedback = {}

if existing_records:
    feedback_response = existing_records[0].feedback_response

    if isinstance(feedback_response, str):
        existing_feedback = json.loads(feedback_response).get("field_feedback", {})
    elif isinstance(feedback_response, dict):
        existing_feedback = feedback_response.get("field_feedback", {})

# Recursively update dirty status for nested data
update_dirty_status(feedback_section, existing_feedback)

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
