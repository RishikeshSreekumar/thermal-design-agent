"""
solid_geometry.py
 
Deterministic solid-geometry calculations for the current
straight plate-fin heat-sink topology.
 
The module calculates physical material volume only.
 
It does not perform:
 
- CAD generation
- Thermal calculations
- Airflow calculations
- Material-density calculations
- Cost estimation
- Optimization or candidate ranking
"""
 
 
def plate_fin_heat_sink_volume(
    base_length_mm: float,
    base_width_mm: float,
    base_thickness_mm: float,
    fin_height_mm: float,
    fin_thickness_mm: float,
    fin_count: int,
) -> float:
    """
    Calculate the total solid material volume of a
    straight plate-fin heat sink.
 
    The current geometry consists of:
 
    - One rectangular base plate
    - Multiple identical rectangular fins
    - Fins positioned on top of the base without
      overlapping the base volume
 
    Parameters
    ----------
    base_length_mm:
        Base and fin length in millimetres.
 
    base_width_mm:
        Base width in millimetres.
 
    base_thickness_mm:
        Base thickness in millimetres.
 
    fin_height_mm:
        Fin height above the base in millimetres.
 
    fin_thickness_mm:
        Thickness of one fin in millimetres.
 
    fin_count:
        Total number of fins.
 
    Returns
    -------
    float
        Total solid heat-sink volume in cubic metres.
 
    Raises
    ------
    ValueError
        If any required dimension is not greater than
        zero or the fin count is less than one.
    """
 
    _validate_plate_fin_geometry(
        base_length_mm=base_length_mm,
        base_width_mm=base_width_mm,
        base_thickness_mm=base_thickness_mm,
        fin_height_mm=fin_height_mm,
        fin_thickness_mm=fin_thickness_mm,
        fin_count=fin_count,
    )
 
    base_volume_mm3 = (
        base_length_mm
        * base_width_mm
        * base_thickness_mm
    )
 
    single_fin_volume_mm3 = (
        base_length_mm
        * fin_thickness_mm
        * fin_height_mm
    )
 
    total_fin_volume_mm3 = (
        fin_count
        * single_fin_volume_mm3
    )
 
    total_volume_mm3 = (
        base_volume_mm3
        + total_fin_volume_mm3
    )
 
    cubic_millimetres_to_cubic_metres = 1e-9
 
    return (
        total_volume_mm3
        * cubic_millimetres_to_cubic_metres
    )
 
 
def _validate_plate_fin_geometry(
    base_length_mm: float,
    base_width_mm: float,
    base_thickness_mm: float,
    fin_height_mm: float,
    fin_thickness_mm: float,
    fin_count: int,
) -> None:
    """
    Validate dimensions required by the plate-fin solid
    volume model.
    """
 
    positive_dimensions = {
        "base_length_mm": base_length_mm,
        "base_width_mm": base_width_mm,
        "base_thickness_mm": base_thickness_mm,
        "fin_height_mm": fin_height_mm,
        "fin_thickness_mm": fin_thickness_mm,
    }
 
    for field_name, value in (
        positive_dimensions.items()
    ):
        if value <= 0.0:
            raise ValueError(
                f"'{field_name}' must be greater "
                "than zero."
            )
 
    if isinstance(fin_count, bool):
        raise ValueError(
            "'fin_count' must be an integer."
        )
 
    if not isinstance(fin_count, int):
        raise ValueError(
            "'fin_count' must be an integer."
        )
 
    if fin_count < 1:
        raise ValueError(
            "'fin_count' must be at least 1."
        )