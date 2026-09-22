from fan.operating_point import SystemResistance
 
 
def main() -> None:
 
    system = SystemResistance(
        resistance_coefficient=2_000_000
    )
 
    assert (
        abs(
            system.pressure_drop(0.0)
        )
        < 1e-9
    )
 
    pressure = system.pressure_drop(0.01)
 
    assert abs(pressure - 200.0) < 1e-9
 
    pressure = system.pressure_drop(0.005)
 
    assert abs(pressure - 50.0) < 1e-9
 
    print("=" * 70)
    print("SYSTEM RESISTANCE TESTS PASSED")
    print("=" * 70)
 
 
if __name__ == "__main__":
    main()