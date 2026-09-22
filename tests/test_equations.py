from core import thermal_equations as eq

rho, mu, k, cp, pr = eq.air_properties(30)

print("rho =", rho)
print("mu =", mu)
print("k =", k)
print("Pr =", pr)

count = eq.fin_count(
    50,
    1,
    3
)

print("Fin Count =", count)

Dh = eq.hydraulic_diameter(
    3,
    25
)

print("Dh =", Dh)

Re = eq.reynolds_number(
    rho,
    5,
    Dh,
    mu
)

print("Re =", Re)

Nu = eq.nusselt_number(
    Re,
    pr
)

print("Nu =", Nu)

h = eq.heat_transfer_coefficient(
    Nu,
    k,
    Dh
)

print("h =", h)

A = eq.total_surface_area(
    50,
    50,
    25,
    1,
    count
)

print("Area =", A)

eta = eq.fin_efficiency(
    h,
    1,
    25
)

print("Fin Efficiency =", eta)

R = eq.thermal_resistance(
    h,
    A,
    eta
)

print("Thermal Resistance =", R)