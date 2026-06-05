import importlib.util
import os
import sys


# Load the advantage engine module directly from file
THIS_DIR = os.path.dirname(__file__)
MODULE_PATH = os.path.abspath(os.path.join(THIS_DIR, '..', 'main.py'))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, '..', '..', '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
spec = importlib.util.spec_from_file_location('advantage_engine_main', MODULE_PATH)
adv_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv_mod)
PivotScoreCalculator = adv_mod.PivotScoreCalculator


def test_pivot_score_typical():
    pivot, confidence, sbi, risk, factors = PivotScoreCalculator.calculate_pivot_score(
        vehicle_make="Toyota",
        vehicle_model="RAV4",
        vehicle_year=2019,
        vehicle_mileage_km=90000,
        listing_price=5_000_000,
    )
    assert 0 <= pivot <= 100
    assert 0.0 <= confidence <= 1.0
    assert isinstance(sbi, int)
    assert hasattr(risk, 'value') or isinstance(risk, str)


def test_pivot_score_old_high_mileage():
    pivot, confidence, sbi, risk, factors = PivotScoreCalculator.calculate_pivot_score(
        vehicle_make="Honda",
        vehicle_model="Civic",
        vehicle_year=2005,
        vehicle_mileage_km=400000,
        listing_price=1_000_000,
    )
    # Expect a below-average pivot score for very old, high-mileage car
    assert pivot < 70
    assert factors["age_years"] >= 15


def test_factors_present():
    pivot, confidence, sbi, risk, factors = PivotScoreCalculator.calculate_pivot_score(
        vehicle_make="Kia",
        vehicle_model="Picanto",
        vehicle_year=2018,
        vehicle_mileage_km=60000,
        listing_price=3_000_000,
    )
    # Ensure new factors are present
    assert "repair_cost_estimate_ugx" in factors
    assert "market_liquidity_score" in factors
    assert "repair_score" in factors
