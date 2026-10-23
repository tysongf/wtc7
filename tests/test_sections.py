from wtc7.sections import col79_section, shape


def test_values_quoted_in_ncstar_1_9():
    g = shape("W33X130")
    assert g.A == 38.3 and g.Iy == 218.0          # §8.7.2, §8.7.4
    assert shape("W24X55").A == 16.2               # §8.7.4


def test_plan_fibres_reproduce_weak_axis_inertia():
    for name in ("W33X130", "W24X55", "W21X44"):
        s = shape(name)
        y, a = s.plan_fibres(24)
        assert abs((a * y**2).sum() - s.Iy) / s.Iy < 1e-9, name
        assert abs(a.sum() - s.A) / s.A < 1e-9, name
        assert a.min() > 0, name


def test_col79_plates_increase_area():
    A2, Imin2, *_ = col79_section(2.0)
    A3, Imin3, *_ = col79_section(3.0)
    assert A2 == 215.0 + 104.0 and A3 == 215.0 + 156.0
    assert Imin3 > Imin2 > shape("W14X730").Iy
