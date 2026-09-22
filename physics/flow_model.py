"""
flow_model.py
 
Flow-area calculations.
 
Responsible for:
 
- gross frontal area
- open flow area
- blockage ratio
- channel velocity
"""

def channel_count(
    fin_count_value: int,
) -> int:
    """
    Return the number of internal flow channels.
 
    For a straight plate-fin heat sink with N fins,
    the current geometry model assumes N - 1 clear
    channels between adjacent fins.
    """
 
    if fin_count_value < 2:
        return 0
 
    return fin_count_value - 1
 
 
def gross_frontal_area(
    base_width_mm: float,
    fin_height_mm: float,
) -> float:
    """
    Return the gross frontal area of the finned region.
 
    This is the total projected area normal to airflow,
    before subtracting blockage caused by the fins.
 
    Returns
    -------
    float
        Gross frontal area in m².
    """
 
    width = base_width_mm / 1000
    height = fin_height_mm / 1000
 
    if width <= 0 or height <= 0:
        return 0.0
 
    return width * height
 
 
def open_flow_area(
    fin_count_value: int,
    fin_spacing_mm: float,
    fin_height_mm: float,
) -> float:
    """
    Return the total open flow area through all fin channels.
 
    The current geometry assumes:
        number of channels = number of fins - 1
 
    Returns
    -------
    float
        Total open channel area in m².
    """
 
    channels = channel_count(
        fin_count_value
    )
 
    spacing = fin_spacing_mm / 1000
    height = fin_height_mm / 1000
 
    if (
        channels <= 0
        or spacing <= 0
        or height <= 0
    ):
        return 0.0
 
    return (
        channels
        * spacing
        * height
    )
 
 
def channel_velocity(
    approach_velocity: float,
    gross_area: float,
    open_area: float,
) -> float:
    """
    Estimate average velocity inside the fin channels.
 
    The calculation applies continuity under the initial
    assumptions that:
 
    - all approach flow enters the fin channels;
    - flow is distributed uniformly;
    - there is no bypass above or around the heat sink;
    - air density change is negligible.
 
    V_channel = V_approach × A_gross / A_open
    """
 
    if approach_velocity <= 0:
        raise ValueError(
            "Approach velocity must be greater than 0 m/s."
        )
 
    if gross_area <= 0:
        raise ValueError(
            "Gross frontal area must be greater than zero."
        )
 
    if open_area <= 0:
        raise ValueError(
            "Open flow area must be greater than zero."
        )
 
    return (
        approach_velocity
        * gross_area
        / open_area
    )
 
 
def blockage_ratio(
    gross_area: float,
    open_area: float,
) -> float:
    """
    Return the fraction of gross frontal area blocked
    by fins.
 
    Returns a value between 0 and 1 for valid geometry.
    """
 
    if gross_area <= 0:
        raise ValueError(
            "Gross frontal area must be greater than zero."
        )
 
    ratio = 1.0 - (
        open_area / gross_area
    )
 
    return max(
        0.0,
        min(1.0, ratio),
    )

