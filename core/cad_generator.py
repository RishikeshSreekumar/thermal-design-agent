"""
cad_generator.py

Creates a plate-fin heat sink using CadQuery
and exports it as a STEP file.
"""

import cadquery as cq

from config import GENERATED_DIR


class CADGenerator:

    def generate(self, geometry):

        # ----------------------------------------------------------
        # Convert mm → mm (CadQuery works naturally in mm)
        # ----------------------------------------------------------

        L = geometry.base_length
        W = geometry.base_width
        B = geometry.base_thickness

        H = geometry.fin_height
        T = geometry.fin_thickness
        S = geometry.fin_spacing

        N = geometry.fin_count

        # ----------------------------------------------------------
        # Base Plate
        # ----------------------------------------------------------

        model = (
            cq.Workplane("XY")
            .box(
                L,
                W,
                B,
                centered=(True, True, False)
            )
        )

        # ----------------------------------------------------------
        # First fin position
        # ----------------------------------------------------------

        total_width = (
            N * T +
            (N - 1) * S
        )

        start_y = -total_width / 2 + T / 2

        # ----------------------------------------------------------
        # Create fins
        # ----------------------------------------------------------

        for i in range(N):

            y = start_y + i * (T + S)

            fin = (
                cq.Workplane("XY")
                .center(0, y)
                .workplane(offset=B)
                .box(
                    L,
                    T,
                    H,
                    centered=(True, True, False)
                )
            )

            model = model.union(fin)

        # ----------------------------------------------------------
        # Export STEP
        # ----------------------------------------------------------

        output_dir = GENERATED_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        step_file = output_dir / "heatsink.step"

        cq.exporters.export(
            model,
            str(step_file)
        )

        print()
        print("STEP exported successfully")
        print(step_file.resolve())

        return step_file