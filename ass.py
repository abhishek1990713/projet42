import json

def update_dirty_status(feedback_section, existing_feedback):
    """
    Recursively compare feedback_section with existing_feedback
    and set 'dirty' = True/False based on changes in 'value' fields.
    Handles nested dicts and lists.
    """
    if isinstance(feedback_section, dict):
        for key, value in feedback_section.items():
            existing_value = existing_feedback.get(key) if isinstance(existing_feedback, dict) else None

            # 1️⃣ If both are dicts → recurse
            if isinstance(value, dict) and isinstance(existing_value, dict):
                update_dirty_status(value, existing_value)

            # 2️⃣ If both are lists → iterate recursively
            elif isinstance(value, list) and isinstance(existing_value, list):
                for i in range(len(value)):
                    if i < len(existing_value):
                        update_dirty_status(value[i], existing_value[i])
                    else:
                        # New item not in existing feedback
                        if isinstance(value[i], dict):
                            value[i]["dirty"] = True

            # 3️⃣ Leaf comparison when both have 'value'
            elif (
                isinstance(value, dict)
                and "value" in value
                and isinstance(existing_value, dict)
                and "value" in existing_value
            ):
                if value["value"] == existing_value["value"]:
                    value["dirty"] = False
                else:
                    value["dirty"] = True

            # 4️⃣ If current value is dict but existing not found → mark dirty
            elif isinstance(value, dict):
                value["dirty"] = True

            # 5️⃣ Ignore pure strings or numbers safely
            else:
                pass

    elif isinstance(feedback_section, list):
        # Handle list at top-level
        for i in range(len(feedback_section)):
            if i < len(existing_feedback):
                update_dirty_status(feedback_section[i], existing_feedback[i])
            else:
                if isinstance(feedback_section[i], dict):
                    feedback_section[i]["dirty"] = True

    return feedback_section


# ---------- MAIN LOGIC ----------
existing_feedback = {}

if existing_records:
    feedback_response = existing_records[0].feedback_response

    if isinstance(feedback_response, str):
        existing_feedback = json.loads(feedback_response).get("field_feedback", {})
    elif isinstance(feedback_response, dict):
        existing_feedback = feedback_response.get("field_feedback", {})

# Run the recursive update
feedback_section = update_dirty_status(feedback_section, existing_feedback)

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
