import inspect

import scripts.bituach_leumi_estimator as estimator


def public_members(module):
    return [
        name
        for name, obj in vars(module).items()
        if not name.startswith("_") and (inspect.isfunction(obj) or inspect.isclass(obj))
    ]


def test_public_surface_count_is_stable():
    names = public_members(estimator)
    assert len(names) >= 10
    assert "BituachLeumiEstimator" in names
    assert "estimate_monthly" in names
    assert "add_vat" in names
