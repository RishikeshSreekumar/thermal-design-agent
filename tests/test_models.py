from models.requirements import (
    EngineeringRequirements,
    Requirements,
    Constraints,
)

req = EngineeringRequirements(

    component_type="heat_sink",

    requirements=Requirements(
        heat_load=165,
        ambient_temperature=30,
        air_velocity=5,
    ),

    constraints=Constraints(
        base_length=50,
        base_width=50,
        max_height=30,
    ),
)

print(req)