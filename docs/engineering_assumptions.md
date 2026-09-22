# Thermal AI Engineer - Engineering Assumptions

## Geometry

- Plate-fin heat sink
- Extruded aluminum construction
- Rectangular straight fins
- Uniform fin thickness
- Uniform fin spacing

## Material

- Aluminium 6063
- Thermal conductivity assumed constant

## Heat Transfer

- Forced convection
- Radiation neglected
- Uniform heat load
- Uniform base temperature

## Air Properties

Air properties assumed constant:

- Density = 1.164 kg/m³
- Dynamic viscosity = 1.872e-5 Pa.s
- Thermal conductivity = 0.0263 W/m.K
- Prandtl number = 0.71

## Correlations

### Reynolds Number

Re = ρVDh/μ

### Nusselt Number

Laminar:

Nu = 7.54

Turbulent:

Nu = 0.023 Re^0.8 Pr^0.4

### Heat Transfer Coefficient

h = Nu*k/Dh

### Fin Efficiency

Straight rectangular fin approximation

### Thermal Resistance

Rth = 1/(h*A*η)

## Optimization

Current Version:

- Height optimization
- Fin spacing optimization

Future Versions:

- Fin thickness optimization
- Pressure drop constraints
- Fan curve integration
- Multi-objective optimization

## CAD

- Parametric CadQuery model
- STEP export