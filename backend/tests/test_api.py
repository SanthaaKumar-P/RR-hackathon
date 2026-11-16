import sys
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.data_loader import data_loader
from app.core.config import settings

client = TestClient(app)

def test_startup_and_data_loader():
    """Verify that all datasets are loaded and cached."""
    data_loader.load_all_datasets()
    assert data_loader._is_loaded is True
    
    batters = data_loader.get_final_batter_rankings()
    assert len(batters) == 266
    
    bowlers = data_loader.get_final_bowler_rankings()
    assert len(bowlers) == 246

def test_health_endpoints():
    """Test /health and /api/v1/health."""
    for url in ["/health", "/api/v1/health"]:
        res = client.get(url)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["datasets_loaded"] is True
        assert data["total_matches"] == 853
        assert data["total_pressure_deliveries"] == 103976

def test_overview_endpoint():
    """Test /api/v1/overview."""
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_matches"] == 853
    assert data["total_selected_deliveries"] == 193988
    assert data["total_pressure_deliveries"] == 103976
    assert data["match_counts"]["T20"] == 371
    assert data["match_counts"]["T20I"] == 482
    assert data["ranked_batters_count"]["total"] == 266
    assert data["ranked_bowlers_count"]["total"] == 246
    assert len(data["top5_batters"]["T20"]) == 5
    assert len(data["top5_bowlers"]["T20"]) == 5

def test_top10_batters_exact_match():
    """Verify API Top 10 batters match outputs/top10_batters_by_format.csv exactly."""
    csv_top10 = pd.read_csv(settings.TOP10_BATTERS_FILE)
    
    for fmt in ["T20", "T20I"]:
        res = client.get(f"/api/v1/batters/top10?format={fmt}")
        assert res.status_code == 200
        api_items = res.json()["items"]
        assert len(api_items) == 10
        
        expected_df = csv_top10[csv_top10["match_format"] == fmt].sort_values("final_rank")
        expected_ids = expected_df["striker_id"].tolist()
        expected_names = expected_df["striker_name"].tolist()
        
        api_ids = [item["striker_id"] for item in api_items]
        api_names = [item["striker_name"] for item in api_items]
        
        assert api_ids == expected_ids, f"Batter Top 10 IDs mismatch for format {fmt}"
        assert api_names == expected_names, f"Batter Top 10 names mismatch for format {fmt}"

def test_top10_bowlers_exact_match():
    """Verify API Top 10 bowlers match outputs/top10_bowlers_by_format.csv exactly."""
    csv_top10 = pd.read_csv(settings.TOP10_BOWLERS_FILE)
    
    for fmt in ["T20", "T20I"]:
        res = client.get(f"/api/v1/bowlers/top10?format={fmt}")
        assert res.status_code == 200
        api_items = res.json()["items"]
        assert len(api_items) == 10
        
        expected_df = csv_top10[csv_top10["match_format"] == fmt].sort_values("final_rank")
        expected_ids = expected_df["bowler_id"].tolist()
        expected_names = expected_df["bowler_name"].tolist()
        
        api_ids = [item["bowler_id"] for item in api_items]
        api_names = [item["bowler_name"] for item in api_items]
        
        assert api_ids == expected_ids, f"Bowler Top 10 IDs mismatch for format {fmt}"
        assert api_names == expected_names, f"Bowler Top 10 names mismatch for format {fmt}"

def test_batter_filtering_search_and_pagination():
    """Test batter list queries."""
    res = client.get("/api/v1/batters?format=T20&page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 109
    assert len(data["items"]) == 10
    assert data["items"][0]["final_rank"] == 1

    # Search by name
    res_search = client.get("/api/v1/batters?format=T20&search=Klaasen")
    assert res_search.status_code == 200
    items = res_search.json()["items"]
    assert len(items) >= 1
    assert "Klaasen" in items[0]["striker_name"]

def test_bowler_filtering_search_and_pagination():
    """Test bowler list queries."""
    res = client.get("/api/v1/bowlers?format=T20&page=1&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 108
    assert len(data["items"]) == 10
    assert data["items"][0]["final_rank"] == 1

    # Search by name
    res_search = client.get("/api/v1/bowlers?format=T20&search=Ngidi")
    assert res_search.status_code == 200
    items = res_search.json()["items"]
    assert len(items) >= 1
    assert "Ngidi" in items[0]["bowler_name"]

def test_single_player_endpoints():
    """Test /api/v1/batters/{id} and /api/v1/bowlers/{id}."""
    # Heinrich Klaasen = 4260
    res_b = client.get("/api/v1/batters/4260?format=T20")
    assert res_b.status_code == 200
    b_data = res_b.json()
    assert b_data["player_id"] == 4260
    assert "Klaasen" in b_data["player_name"]
    assert b_data["ranking"]["final_rank"] == 1

    # Lungi Ngidi = 4641
    res_w = client.get("/api/v1/bowlers/4641?format=T20")
    assert res_w.status_code == 200
    w_data = res_w.json()
    assert w_data["player_id"] == 4641
    assert "Ngidi" in w_data["player_name"]
    assert w_data["ranking"]["final_rank"] == 1
    assert w_data["accounting_sensitivity"] is not None

    # Unknown player returns 404
    res_404 = client.get("/api/v1/batters/99999999?format=T20")
    assert res_404.status_code == 404

def test_pressure_analytics():
    """Test pressure analytics endpoints."""
    res_sum = client.get("/api/v1/pressure/summary?format=T20")
    assert res_sum.status_code == 200
    assert res_sum.json()["pressure_deliveries"] > 0

    res_cat = client.get("/api/v1/pressure/categories")
    assert res_cat.status_code == 200
    categories = [c["category"] for c in res_cat.json()]
    assert "Extreme" in categories
    assert "High" in categories
    assert "Moderate" in categories

    res_phases = client.get("/api/v1/pressure/phases")
    assert res_phases.status_code == 200
    phases = [p["phase"] for p in res_phases.json()]
    assert "Powerplay" in phases
    assert "Middle" in phases
    assert "Death" in phases

def test_matches_endpoints():
    """Test matches endpoints."""
    res_m = client.get("/api/v1/matches?limit=5")
    assert res_m.status_code == 200
    matches = res_m.json()["items"]
    assert len(matches) == 5

    match_id = matches[0]["match_id"]
    res_single = client.get(f"/api/v1/matches/{match_id}")
    assert res_single.status_code == 200
    assert res_single.json()["match_id"] == match_id

    res_inn = client.get(f"/api/v1/matches/{match_id}/innings")
    assert res_inn.status_code == 200

    res_timeline = client.get(f"/api/v1/matches/{match_id}/pressure-timeline")
    assert res_timeline.status_code == 200
    t_data = res_timeline.json()
    assert "overs" in t_data
    assert "deliveries" in t_data

def test_player_comparison():
    """Test compare endpoints."""
    # Compare Heinrich Klaasen (4260) and Suryakumar Yadav (1699)
    res_b = client.get("/api/v1/compare/batters?player_ids=4260,1699&format=T20")
    assert res_b.status_code == 200
    b_data = res_b.json()
    assert len(b_data["players"]) == 2
    assert len(b_data["metric_matrix"]) > 5

    # Compare Lungi Ngidi (4641) and Matheesha Pathirana (8661)
    res_w = client.get("/api/v1/compare/bowlers?player_ids=4641,8661&format=T20")
    assert res_w.status_code == 200
    w_data = res_w.json()
    assert len(w_data["players"]) == 2
    assert len(w_data["metric_matrix"]) > 5

def test_methodology():
    """Test /api/v1/methodology."""
    res = client.get("/api/v1/methodology")
    assert res.status_code == 200
    data = res.json()
    assert "eligibility_thresholds" in data
    assert "batter_baseline_weights" in data
    assert "bowler_baseline_weights" in data
    assert "wicket_credit_rules" in data

def test_scenarios():
    """Test /api/v1/scenarios/batters and /bowlers."""
    res_b = client.get("/api/v1/scenarios/batters?format=T20")
    assert res_b.status_code == 200
    b_data = res_b.json()
    assert "Baseline" in b_data["scenario_rankings"]
    assert "Volume_Focused" in b_data["scenario_rankings"]
    assert "Efficiency_Focused" in b_data["scenario_rankings"]

    res_w = client.get("/api/v1/scenarios/bowlers?format=T20")
    assert res_w.status_code == 200
    w_data = res_w.json()
    assert "Baseline" in w_data["scenario_rankings"]
    assert "Wicket_Impact" in w_data["scenario_rankings"]
    assert "Control_Focused" in w_data["scenario_rankings"]
    assert "accounting_sensitivity_summary" in w_data

def test_audit_endpoints():
    """Test /api/v1/audit/summary and /data-quality."""
    res_sum = client.get("/api/v1/audit/summary")
    assert res_sum.status_code == 200
    s_data = res_sum.json()
    assert s_data["passed_count"] > 0
    assert s_data["warning_count"] > 0
    assert s_data["not_verified_count"] > 0
    
    # Check that statuses are strictly PASS, WARNING, NOT VERIFIED
    for audit in s_data["audits"]:
        assert audit["status"] in ["PASS", "WARNING", "NOT VERIFIED"]

    res_dq = client.get("/api/v1/audit/data-quality")
    assert res_dq.status_code == 200
    dq_data = res_dq.json()
    assert len(dq_data["tables"]) > 0
    assert len(dq_data["limitations"]) > 0

if __name__ == "__main__":
    print("Running API test suite...")
    test_startup_and_data_loader()
    print("✓ Startup and DataLoader passed")
    test_health_endpoints()
    print("✓ Health endpoints passed")
    test_overview_endpoint()
    print("✓ Overview endpoint passed")
    test_top10_batters_exact_match()
    print("✓ Top 10 Batters EXACT match verified")
    test_top10_bowlers_exact_match()
    print("✓ Top 10 Bowlers EXACT match verified")
    test_batter_filtering_search_and_pagination()
    print("✓ Batter filtering, search & pagination passed")
    test_bowler_filtering_search_and_pagination()
    print("✓ Bowler filtering, search & pagination passed")
    test_single_player_endpoints()
    print("✓ Single player lookup passed")
    test_pressure_analytics()
    print("✓ Pressure analytics passed")
    test_matches_endpoints()
    print("✓ Matches endpoints passed")
    test_player_comparison()
    print("✓ Player comparison passed")
    test_methodology()
    print("✓ Methodology passed")
    test_scenarios()
    print("✓ Scenarios passed")
    test_audit_endpoints()
    print("✓ Audit endpoints passed")
    print("\nALL 14 TEST SUITES PASSED PERFECTLY!")
