"""Comprehensive unit tests for the Superstore BI Platform."""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    yield client


# ============================================================
#  AUTH TESTS
# ============================================================

class TestAuthentication:
    def test_login_page_renders(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_login_success(self, client):
        r = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
        assert r.status_code == 302

    def test_login_failure(self, client):
        r = client.post("/login", data={"username": "admin", "password": "wrong"}, follow_redirects=False)
        assert r.status_code == 200

    def test_logout(self, auth_client):
        r = auth_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302

    def test_protected_route_redirects(self, client):
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code == 302

    def test_all_demo_users_login(self, client):
        for user, pw in [("admin", "admin123"), ("analyst", "analyst123"), ("manager", "manager123"), ("executive", "executive123")]:
            c = app.test_client()
            r = c.post("/login", data={"username": user, "password": pw}, follow_redirects=False)
            assert r.status_code == 302


# ============================================================
#  PAGE ROUTE TESTS
# ============================================================

class TestPages:
    def test_dashboard(self, auth_client):
        r = auth_client.get("/dashboard")
        assert r.status_code == 200

    def test_dashboard_root(self, auth_client):
        r = auth_client.get("/")
        assert r.status_code == 200

    def test_analytics(self, auth_client):
        r = auth_client.get("/analytics")
        assert r.status_code == 200

    def test_products(self, auth_client):
        r = auth_client.get("/products")
        assert r.status_code == 200

    def test_customers(self, auth_client):
        r = auth_client.get("/customers")
        assert r.status_code == 200

    def test_regions(self, auth_client):
        r = auth_client.get("/regions")
        assert r.status_code == 200

    def test_profit(self, auth_client):
        r = auth_client.get("/profit")
        assert r.status_code == 200

    def test_insights(self, auth_client):
        r = auth_client.get("/insights")
        assert r.status_code == 200

    def test_forecasting(self, auth_client):
        r = auth_client.get("/forecasting")
        assert r.status_code == 200

    def test_whatif(self, auth_client):
        r = auth_client.get("/what-if")
        assert r.status_code == 200

    def test_customer_analytics(self, auth_client):
        r = auth_client.get("/customer-analytics")
        assert r.status_code == 200

    def test_chatbot(self, auth_client):
        r = auth_client.get("/chatbot")
        assert r.status_code == 200

    def test_upload(self, auth_client):
        r = auth_client.get("/upload")
        assert r.status_code == 200

    def test_reports(self, auth_client):
        r = auth_client.get("/reports")
        assert r.status_code == 200

    def test_admin(self, auth_client):
        r = auth_client.get("/admin")
        assert r.status_code == 200

    def test_builder(self, auth_client):
        r = auth_client.get("/builder")
        assert r.status_code == 200

    def test_settings(self, auth_client):
        r = auth_client.get("/settings")
        assert r.status_code == 200

    def test_search(self, auth_client):
        r = auth_client.get("/search")
        assert r.status_code == 200

    def test_404_page(self, client):
        r = client.get("/nonexistent-page")
        assert r.status_code == 404


# ============================================================
#  API TESTS
# ============================================================

class TestAPIs:
    def test_kpis(self, auth_client):
        r = auth_client.get("/api/kpis")
        assert r.status_code == 200
        data = r.get_json()
        assert "total_sales" in data
        assert "total_profit" in data

    def test_kpi_comparisons(self, auth_client):
        r = auth_client.get("/api/kpi-comparisons")
        assert r.status_code == 200

    def test_sales_trend(self, auth_client):
        r = auth_client.get("/api/sales-trend")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_category_sales(self, auth_client):
        r = auth_client.get("/api/category-sales")
        assert r.status_code == 200

    def test_region_sales(self, auth_client):
        r = auth_client.get("/api/region-sales")
        assert r.status_code == 200

    def test_segment_analysis(self, auth_client):
        r = auth_client.get("/api/segment-analysis")
        assert r.status_code == 200

    def test_top_products(self, auth_client):
        r = auth_client.get("/api/top-products")
        assert r.status_code == 200

    def test_bottom_products(self, auth_client):
        r = auth_client.get("/api/bottom-products")
        assert r.status_code == 200

    def test_state_performance(self, auth_client):
        r = auth_client.get("/api/state-performance")
        assert r.status_code == 200

    def test_shipping_analysis(self, auth_client):
        r = auth_client.get("/api/shipping-analysis")
        assert r.status_code == 200

    def test_discount_impact(self, auth_client):
        r = auth_client.get("/api/discount-impact")
        assert r.status_code == 200

    def test_sub_category_sales(self, auth_client):
        r = auth_client.get("/api/sub-category-sales")
        assert r.status_code == 200

    def test_customer_analysis(self, auth_client):
        r = auth_client.get("/api/customer-analysis")
        assert r.status_code == 200

    def test_profit_margin_by_category(self, auth_client):
        r = auth_client.get("/api/profit-margin-by-category")
        assert r.status_code == 200

    def test_scatter_data(self, auth_client):
        r = auth_client.get("/api/scatter-data")
        assert r.status_code == 200

    def test_radar_data(self, auth_client):
        r = auth_client.get("/api/radar-data")
        assert r.status_code == 200

    def test_year_over_year(self, auth_client):
        r = auth_client.get("/api/year-over-year")
        assert r.status_code == 200

    def test_dashboard_data(self, auth_client):
        r = auth_client.get("/api/dashboard-data")
        assert r.status_code == 200
        data = r.get_json()
        assert "kpis" in data

    def test_filter_options(self, auth_client):
        r = auth_client.get("/api/filter-options")
        assert r.status_code == 200
        data = r.get_json()
        assert "years" in data
        assert "categories" in data

    def test_executive_summary(self, auth_client):
        r = auth_client.get("/api/executive-summary")
        assert r.status_code == 200
        data = r.get_json()
        assert "health_score" in data
        assert "ai_summary" in data

    def test_insights(self, auth_client):
        r = auth_client.get("/api/insights")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_drilldown(self, auth_client):
        r = auth_client.get("/api/drilldown?level=categories")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_drilldown_subcategories(self, auth_client):
        r = auth_client.get("/api/drilldown?level=subcategories&parent=Furniture")
        assert r.status_code == 200

    def test_drilldown_products(self, auth_client):
        r = auth_client.get("/api/drilldown?level=products&parent=Chairs")
        assert r.status_code == 200

    def test_forecast(self, auth_client):
        r = auth_client.get("/api/forecast?metric=sales&months=3")
        assert r.status_code == 200
        data = r.get_json()
        assert "sales" in data

    def test_forecast_all(self, auth_client):
        r = auth_client.get("/api/forecast?metric=all&months=6")
        assert r.status_code == 200
        data = r.get_json()
        assert "sales" in data
        assert "profit" in data

    def test_legacy_forecast(self, auth_client):
        r = auth_client.get("/api/legacy-forecast?months=3")
        assert r.status_code == 200

    def test_chat(self, auth_client):
        r = auth_client.post("/api/chat", json={"question": "What are top selling products?"})
        assert r.status_code == 200
        data = r.get_json()
        assert "answer" in data
        assert "data" in data

    def test_chat_empty(self, auth_client):
        r = auth_client.post("/api/chat", json={"question": ""})
        assert r.status_code == 400

    def test_chat_profit(self, auth_client):
        r = auth_client.post("/api/chat", json={"question": "Show profit by region"})
        assert r.status_code == 200

    def test_chat_customer(self, auth_client):
        r = auth_client.post("/api/chat", json={"question": "Customer analysis by segment"})
        assert r.status_code == 200

    def test_chat_forecast(self, auth_client):
        r = auth_client.post("/api/chat", json={"question": "Forecast sales trend"})
        assert r.status_code == 200

    def test_whatif(self, auth_client):
        r = auth_client.post("/api/what-if", json={"discount_change": 10, "price_change": 5, "volume_change": 15})
        assert r.status_code == 200
        data = r.get_json()
        assert "current" in data
        assert "projected" in data

    def test_customer_analytics_rfm(self, auth_client):
        r = auth_client.post("/api/customer-analytics", json={"type": "rfm"})
        assert r.status_code == 200
        data = r.get_json()
        assert "segments" in data

    def test_customer_analytics_clv(self, auth_client):
        r = auth_client.post("/api/customer-analytics", json={"type": "clv"})
        assert r.status_code == 200
        data = r.get_json()
        assert "customers" in data

    def test_customer_analytics_churn(self, auth_client):
        r = auth_client.post("/api/customer-analytics", json={"type": "churn"})
        assert r.status_code == 200
        data = r.get_json()
        assert "customers" in data
        assert "summary" in data

    def test_customer_analytics_clusters(self, auth_client):
        r = auth_client.post("/api/customer-analytics", json={"type": "clusters"})
        assert r.status_code == 200
        data = r.get_json()
        assert "clusters" in data

    def test_customer_analytics_invalid(self, auth_client):
        r = auth_client.post("/api/customer-analytics", json={"type": "invalid"})
        assert r.status_code == 400

    def test_search(self, auth_client):
        r = auth_client.get("/api/search?q=phone")
        assert r.status_code == 200
        data = r.get_json()
        assert "results" in data

    def test_search_empty(self, auth_client):
        r = auth_client.get("/api/search?q=")
        assert r.status_code == 200

    def test_notifications(self, auth_client):
        r = auth_client.get("/api/notifications")
        assert r.status_code == 200

    def test_notifications_unread(self, auth_client):
        r = auth_client.get("/api/notifications?unread=true")
        assert r.status_code == 200

    def test_notification_mark_read(self, auth_client):
        r = auth_client.post("/api/notifications/read/1")
        assert r.status_code == 200

    def test_notification_mark_all(self, auth_client):
        r = auth_client.post("/api/notifications/read-all")
        assert r.status_code == 200

    def test_users_list(self, auth_client):
        r = auth_client.get("/api/users")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_audit_logs(self, auth_client):
        r = auth_client.get("/api/audit-logs")
        assert r.status_code == 200

    def test_activity_log(self, auth_client):
        r = auth_client.get("/api/activity-log")
        assert r.status_code == 200

    def test_data_profile(self, auth_client):
        r = auth_client.get("/api/data-profile")
        assert r.status_code == 200
        data = r.get_json()
        assert "row_count" in data

    def test_bookmarks_crud(self, auth_client):
        r = auth_client.post("/api/bookmarks", json={"page": "/dashboard", "name": "Test Bookmark"})
        assert r.status_code == 200
        r = auth_client.get("/api/bookmarks")
        assert r.status_code == 200
        bms = r.get_json()
        assert len(bms) >= 1
        r = auth_client.delete("/api/bookmarks/" + str(bms[0]["id"]))
        assert r.status_code == 200


# ============================================================
#  ROLE-BASED ACCESS TESTS
# ============================================================

class TestRBAC:
    def test_admin_required_for_admin_page(self, client):
        client.post("/login", data={"username": "analyst", "password": "analyst123"})
        r = client.get("/admin", follow_redirects=False)
        assert r.status_code == 302

    def test_non_admin_cannot_manage_users(self, client):
        client.post("/login", data={"username": "analyst", "password": "analyst123"})
        r = client.get("/api/users")
        assert r.status_code == 403

    def test_non_admin_cannot_access_audit(self, client):
        client.post("/login", data={"username": "manager", "password": "manager123"})
        r = client.get("/api/audit-logs")
        assert r.status_code == 403

    def test_admin_can_access_all(self, auth_client):
        r = auth_client.get("/api/users")
        assert r.status_code == 200

    def test_api_returns_401_without_login(self, client):
        r = client.get("/api/kpis")
        assert r.status_code == 401


# ============================================================
#  SERVICE UNIT TESTS
# ============================================================

class TestServices:
    def test_auth_service_login(self):
        from services.auth_service import login_user
        user = login_user("admin", "admin123")
        assert user is not None
        assert user["role"] == "admin"

    def test_auth_service_login_fail(self):
        from services.auth_service import login_user
        user = login_user("admin", "wrong")
        assert user is None

    def test_auth_service_get_user(self):
        from services.auth_service import get_user_by_id
        user = get_user_by_id(1)
        assert user is not None
        assert user["username"] == "admin"

    def test_auth_service_get_all_users(self):
        from services.auth_service import get_all_users
        users = get_all_users()
        assert len(users) == 4

    def test_analytics_service_dashboard(self):
        from services.analytics_service import get_dashboard_data
        data = get_dashboard_data()
        assert "kpis" in data

    def test_analytics_service_executive_summary(self):
        from services.analytics_service import get_executive_summary
        summary = get_executive_summary()
        assert "health_score" in summary
        assert 0 <= summary["health_score"] <= 100

    def test_analytics_health_score(self):
        from services.analytics_service import calculate_health_score
        assert calculate_health_score({"total_sales": 200000, "total_profit": 40000, "profit_margin": 20, "avg_order_value": 600}) > 70
        assert calculate_health_score({"total_sales": 0, "total_profit": -1000, "profit_margin": -15, "avg_order_value": 0}) < 40

    def test_forecast_service(self):
        from services.forecast_service import forecast_sales, forecast_profit, forecast_customers
        s = forecast_sales(months_ahead=3)
        assert "predicted" in s
        p = forecast_profit(months_ahead=3)
        assert "predicted" in p
        cu = forecast_customers(months_ahead=3)
        assert "predicted" in cu

    def test_chatbot_service(self):
        from services.chatbot_service import process_query
        r = process_query("What are top selling products?")
        assert r["intent"] == "top_products"
        assert len(r["answer"]) > 0

    def test_chatbot_intents(self):
        from services.chatbot_service import process_query
        assert process_query("Show sales data")["intent"] == "sales_query"
        assert process_query("Analyze profit margin")["intent"] == "profit_query"
        assert process_query("Show Maharashtra state data")["intent"] == "regional_analysis"
        assert process_query("Customer segments")["intent"] == "customer_analysis"

    def test_upload_service_validate(self):
        from services.upload_service import validate_csv
        csv_path = os.path.join(os.path.dirname(__file__), "dataset", "Superstore.csv")
        result = validate_csv(csv_path)
        assert result["valid"]

    def test_upload_service_profile(self):
        from services.upload_service import get_data_profile
        profile = get_data_profile()
        assert profile["row_count"] > 0

    def test_notification_service(self):
        from services.notification_service import get_notifications, get_unread_count, create_notification
        notifs = get_notifications(1)
        assert len(notifs) >= 0
        count = get_unread_count(1)
        assert count >= 0


# ============================================================
#  ANALYTICS ENGINE TESTS
# ============================================================

class TestAnalyticsEngine:
    def test_kpis(self):
        from utils.analytics import get_kpis
        kpis = get_kpis()
        assert "total_sales" in kpis
        assert "total_profit" in kpis

    def test_kpi_comparisons(self):
        from utils.analytics import get_kpi_comparisons
        comp = get_kpi_comparisons()
        assert "total_sales" in comp

    def test_sales_trend(self):
        from utils.analytics import get_sales_trend
        trend = get_sales_trend()
        assert isinstance(trend, list)
        assert len(trend) > 0

    def test_category_sales(self):
        from utils.analytics import get_category_sales
        cats = get_category_sales()
        assert len(cats) >= 1

    def test_region_sales(self):
        from utils.analytics import get_region_sales
        regions = get_region_sales()
        assert len(regions) >= 1

    def test_segment_analysis(self):
        from utils.analytics import get_segment_analysis
        segs = get_segment_analysis()
        assert len(segs) >= 1

    def test_top_products(self):
        from utils.analytics import get_top_products
        prods = get_top_products(limit=5)
        assert len(prods) <= 5

    def test_bottom_products(self):
        from utils.analytics import get_bottom_products
        prods = get_bottom_products(limit=5)
        assert len(prods) <= 5

    def test_state_performance(self):
        from utils.analytics import get_state_performance
        states = get_state_performance()
        assert len(states) >= 1

    def test_forecast(self):
        from utils.analytics import get_forecast
        fc = get_forecast(months_ahead=3)
        assert len(fc["labels"]) == 3

    def test_drilldown(self):
        from utils.analytics import get_drilldown
        cats = get_drilldown("categories")
        assert len(cats) >= 1
        sub = get_drilldown("subcategories", parent_value="Furniture")
        assert isinstance(sub, list)

    def test_insights(self):
        from utils.analytics import generate_insights
        ins = generate_insights()
        assert isinstance(ins, list)
        assert len(ins) > 0

    def test_filter_options(self):
        from utils.analytics import get_filter_options
        opts = get_filter_options()
        assert "years" in opts
        assert "categories" in opts

    def test_safe_float(self):
        from utils.analytics import safe_float
        assert safe_float("123.45") == 123.45
        assert safe_float(None) == 0.0
        assert safe_float("abc") == 0.0
        assert safe_float(42) == 42.0

    def test_filtered_data(self):
        from utils.analytics import get_filtered_data
        where, params = get_filtered_data({"year": "2022", "category": "Technology"})
        assert "2022" in params
        assert "Technology" in params

    def test_scatter_data(self):
        from utils.analytics import get_scatter_data
        data = get_scatter_data()
        assert isinstance(data, list)

    def test_radar_data(self):
        from utils.analytics import get_radar_data
        data = get_radar_data()
        assert isinstance(data, list)

    def test_shipping_analysis(self):
        from utils.analytics import get_shipping_analysis
        data = get_shipping_analysis()
        assert isinstance(data, list)

    def test_discount_impact(self):
        from utils.analytics import get_discount_impact
        data = get_discount_impact()
        assert isinstance(data, list)


# ============================================================
#  EXPORT TESTS
# ============================================================

class TestExports:
    def test_csv_export(self, auth_client):
        r = auth_client.get("/api/export/csv")
        assert r.status_code == 200

    def test_excel_export(self, auth_client):
        r = auth_client.get("/api/export/excel")
        assert r.status_code == 200


# ============================================================
#  ERROR HANDLING TESTS
# ============================================================

class TestErrors:
    def test_404(self, client):
        r = client.get("/nonexistent")
        assert r.status_code == 404

    def test_404_api(self, client):
        r = client.get("/api/nonexistent")
        assert r.status_code in (401, 404)

    def test_chat_missing_question(self, auth_client):
        r = auth_client.post("/api/chat", json={})
        assert r.status_code == 400
