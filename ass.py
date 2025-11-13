import json
import logging

logger = logging.getLogger(__name__)

def update_dirty_status(feedback_section, existing_feedback):
    """
    Recursively update the 'dirty' status in the feedback_section
    based on the values present in existing_feedback.

    Args:
        feedback_section (dict or list): New feedback data to update.
        existing_feedback (dict or list): Existing feedback data to compare with.
    """

    # Handle dictionary-level recursion
    if isinstance(feedback_section, dict):
        for key, value in feedback_section.items():
            if key in existing_feedback:
                if isinstance(value, dict) and isinstance(existing_feedback[key], dict):
                    # Recursively handle nested dictionaries
                    update_dirty_status(value, existing_feedback[key])

                elif isinstance(value, list) and isinstance(existing_feedback[key], list):
                    # Recursively handle lists
                    for index, item in enumerate(value):
                        if index < len(existing_feedback[key]):
                            update_dirty_status(item, existing_feedback[key][index])
                        else:
                            # Mark as dirty if index out of bounds
                            if isinstance(item, dict):
                                item["dirty"] = True

                elif (
                    isinstance(value, dict)
                    and "value" in value
                    and isinstance(existing_feedback[key], dict)
                    and "value" in existing_feedback[key]
                ):
                    # Compare values for non-nested fields
                    value["dirty"] = value["value"] != existing_feedback[key]["value"]

                else:
                    # Skip unexpected structure
                    continue
            else:
                # Mark as dirty if key not present in existing feedback
                if isinstance(value, dict):
                    value["dirty"] = True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            item["dirty"] = True

    # Handle list-level recursion
    elif isinstance(feedback_section, list):
        for index, item in enumerate(feedback_section):
            if index < len(existing_feedback):
                update_dirty_status(item, existing_feedback[index])
            else:
                # Mark as dirty if index out of bounds
                if isinstance(item, dict):
                    item["dirty"] = True


def apply_dirty_status(feedback_section, existing_records):
    """
    Apply the 'dirty' status update on the feedback_section based on existing_records.

    Args:
        feedback_section (dict): New feedback data.
        existing_records (list): List of existing DB records (query result).
    """

    if existing_records:
        feedback_response = existing_records[0].feedback_response

        # Convert string JSON to dict
        if isinstance(feedback_response, str):
            existing_feedback = json.loads(feedback_response).get("field_feedback", {})
        elif isinstance(feedback_response, dict):
            existing_feedback = feedback_response.get("field_feedback", {})
        else:
            existing_feedback = {}

        # Update dirty status recursively
        update_dirty_status(feedback_section, existing_feedback)

        if logger:
            logger.info(f"Updated feedback_section with dirty status: {json.dumps(feedback_section, indent=4)}")

    else:
        # No existing records → mark all fields dirty
        for key, value in feedback_section.items():
            if isinstance(value, dict):
                value["dirty"] = True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        item["dirty"] = True

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
