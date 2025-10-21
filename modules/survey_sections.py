# census_app/modules/survey_sections.py

"""
This module provides survey section functions for the NACP app.
All dynamic section loading is handled via survey_helpers.py to avoid circular imports.
"""

from census_app.modules.survey_helpers import (
    show_regular_survey_section,
    get_completed_sections,
    mark_section_complete
)

# Optional helpers (if not yet implemented, we create stubs)
try:
    from census_app.modules.survey_helpers import get_total_sections
except ImportError:
    def get_total_sections():
        # Default: 3 sections for now
        return 3

try:
    from census_app.modules.survey_helpers import get_holder_name
except ImportError:
    def get_holder_name(holder_id: int):
        return f"Holder {holder_id}"

try:
    from census_app.modules.survey_helpers import get_holder_info
except ImportError:
    def get_holder_info(holder_id: int):
        return {}

# ------------------- Section Constants -------------------
SURVEY_SECTION_LABELS = {
    1: "Holder Information",
    2: "Holding Labour Form",
    3: "Holding Labour Permanent",
    # Add more sections as needed
}

# ------------------- Section Interface Functions -------------------

def render_section(section_id: int, holder_id: int):
    """
    Render a survey section dynamically for the given holder.
    This is the function that survey_sidebar.py or other callers can invoke.
    """
    show_regular_survey_section(section_id, holder_id)

def get_completed(holder_id: int):
    """
    Get completed survey sections for a given holder.
    Returns a set of section IDs.
    """
    return get_completed_sections(holder_id)

def complete_section(holder_id: int, section_id: int):
    """
    Mark a survey section as completed.
    """
    mark_section_complete(holder_id, section_id)

def get_section_label(section_id: int) -> str:
    """
    Return the label of a section for UI purposes.
    """
    return SURVEY_SECTION_LABELS.get(section_id, f"Section {section_id}")

def list_all_sections():
    """
    Return a list of all section IDs.
    """
    return list(range(1, get_total_sections() + 1))
