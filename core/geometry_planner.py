"""
geometry_planner.py

Converts ThermalResults into CAD geometry.
"""

from models.geometry import GeometryParameters


class GeometryPlanner:

    def create_geometry(
        self,
        requirements,
        thermal_results
    ):

        return GeometryParameters(

            base_length=requirements.constraints.base_length,

            base_width=requirements.constraints.base_width,

            base_thickness=thermal_results.base_thickness,

            fin_count=thermal_results.fin_count,

            fin_height=thermal_results.fin_height,

            fin_thickness=thermal_results.fin_thickness,

            fin_spacing=thermal_results.fin_spacing,

            material=thermal_results.material

        )