"""
Stellium Web - Birth Input Component

Form for entering birth data with the astro-charts conversational style.
Now uses the unified component with manual/notable toggle.
"""

from components.birth_input_unified import create_unified_birth_input
from state import ChartState


def create_birth_input_form(state: ChartState, on_change=None):
    """
    Create the birth data input form.

    Args:
        state: ChartState instance to bind to
        on_change: Optional callback when any field changes
    """
    create_unified_birth_input(
        state=state,
        on_change=on_change,
        label="BIRTH DETAILS",
        show_notable_toggle=True,
    )
