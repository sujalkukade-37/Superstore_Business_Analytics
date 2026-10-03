"""Superstore Business Intelligence Platform - Application Factory."""

import os
import sys
import logging
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config_by_name
from models.database import init_db, query_db, execute_db, get_db_connection
from utils.decorators import login_required, role_required, admin_required
from utils.analytics import (
    get_kpis, get_kpi_comparisons, get_sales_trend, get_category_sales,
    get_region_sales, get_segment_analysis, get_top_products, get_bottom_products,
    get_state_performance, get_shipping_analysis, get_discount_impact,
    get_sub_category_sales, get_customer_analysis, get_profit_margin_by_category,
    get_year_over_year, get_scatter_data, get_radar_data, get_forecast,
    get_drilldown, generate_insights, get_filter_options, safe_float,
)
from services.auth_service import (
    login_user, get_user_by_id, get_all_users, create_user,
    update_user, delete_user, change_password, log_audit, log_activity,
    get_audit_logs, get_activity_log,
)
from services.analytics_service import (
    get_dashboard_data, get_executive_summary, get_full_insights,
)
from services.forecast_service import forecast_sales, forecast_profit, forecast_customers
from services.chatbot_service import process_query
from services.upload_service import validate_csv, import_to_database, get_data_profile
from services.report_service import generate_excel_report, generate_csv_export
from services.notification_service import (
    get_notifications, mark_read, mark_all_read, create_notification, get_unread_count,
)

env = os.environ.get("FLASK_ENV", "development")
app = Flask(__name__)
app.config.from_object(config_by_name.get(env, config_by_name["development"]))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
os.makedirs(app.config.get("EXPORT_FOLDER", "exports"), exist_ok=True)

with app.app_context():
    init_db()


@app.teardown_appcontext
def close_db(exception):
    from flask import g
    db = g.pop("_db", None)
    if db is not None:
        db.close()


@app.context_processor
def inject_globals():
    user = None
    unread = 0
    if session.get("logged_in"):
        user = get_user_by_id(session.get("user_id"))
        unread = get_unread_count(session.get("user_id"))
    return dict(
        current_user=user,
        unread_notifications=unread,
        now=datetime.now(),
    )


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("errors/500.html"), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard_page"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = login_user(username, password)
        if user:
            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["full_name"] = user["full_name"]
            log_audit(user["id"], "login", "auth", f"{user['username']} logged in", request.remote_addr)
            log_activity(user["id"], "login", f"{user['username']} logged in")
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("dashboard_page"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    username = session.get("username", "unknown")
    if user_id:
        log_audit(user_id, "logout", "auth", f"{username} logged out", request.remote_addr)
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard_page():
    options = get_filter_options()
    return render_template("dashboard.html", options=options)


@app.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")


@app.route("/products")
@login_required
def products_page():
    return render_template("products.html")


@app.route("/customers")
@login_required
def customers_page():
    return render_template("customers.html")


@app.route("/regions")
@login_required
def regions_page():
    return render_template("regions.html")


@app.route("/profit")
@login_required
def profit_page():
    return render_template("profit.html")


@app.route("/insights")
@login_required
def insights_page():
    return render_template("insights.html")


@app.route("/forecasting")
@login_required
def forecasting_page():
    return render_template("forecasting.html")


@app.route("/what-if")
@login_required
def whatif_page():
    return render_template("whatif.html")


@app.route("/customer-analytics")
@login_required
def customer_analytics_page():
    return render_template("customer_analytics.html")


@app.route("/chatbot")
@login_required
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/upload")
@login_required
@role_required("admin", "analyst")
def upload_page():
    return render_template("upload.html")


@app.route("/reports")
@login_required
def reports_page():
    return render_template("reports.html")


@app.route("/admin")
@login_required
@admin_required
def admin_page():
    return render_template("admin.html")


@app.route("/builder")
@login_required
def builder_page():
    return render_template("builder.html")


@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html")


@app.route("/search")
@login_required
def search_page():
    return render_template("search.html")


# ============================================================
#  API ROUTES
# ============================================================

@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    filters = {
        "year": request.args.get("year"),
        "month": request.args.get("month"),
        "category": request.args.get("category"),
        "region": request.args.get("region"),
        "segment": request.args.get("segment"),
        "state": request.args.get("state"),
        "ship_mode": request.args.get("ship_mode"),
        "quarter": request.args.get("quarter"),
    }
    filters = {k: v for k, v in filters.items() if v}
    data = get_dashboard_data(filters)
    return jsonify(data)


@app.route("/api/kpis")
@login_required
def api_kpis():
    filters = _parse_filters()
    return jsonify(get_kpis(filters))


@app.route("/api/kpi-comparisons")
@login_required
def api_kpi_comparisons():
    filters = _parse_filters()
    return jsonify(get_kpi_comparisons(filters))


@app.route("/api/sales-trend")
@login_required
def api_sales_trend():
    filters = _parse_filters()
    return jsonify(get_sales_trend(filters))


@app.route("/api/category-sales")
@login_required
def api_category_sales():
    filters = _parse_filters()
    return jsonify(get_category_sales(filters))


@app.route("/api/region-sales")
@login_required
def api_region_sales():
    filters = _parse_filters()
    return jsonify(get_region_sales(filters))


@app.route("/api/segment-analysis")
@login_required
def api_segment_analysis():
    filters = _parse_filters()
    return jsonify(get_segment_analysis(filters))


@app.route("/api/top-products")
@login_required
def api_top_products():
    filters = _parse_filters()
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_top_products(filters, limit))


@app.route("/api/bottom-products")
@login_required
def api_bottom_products():
    filters = _parse_filters()
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_bottom_products(filters, limit))


@app.route("/api/state-performance")
@login_required
def api_state_performance():
    filters = _parse_filters()
    return jsonify(get_state_performance(filters))


@app.route("/api/shipping-analysis")
@login_required
def api_shipping_analysis():
    filters = _parse_filters()
    return jsonify(get_shipping_analysis(filters))


@app.route("/api/discount-impact")
@login_required
def api_discount_impact():
    filters = _parse_filters()
    return jsonify(get_discount_impact(filters))


@app.route("/api/sub-category-sales")
@login_required
def api_sub_category_sales():
    filters = _parse_filters()
    return jsonify(get_sub_category_sales(filters))


@app.route("/api/customer-analysis")
@login_required
def api_customer_analysis():
    filters = _parse_filters()
    return jsonify(get_customer_analysis(filters))


@app.route("/api/profit-margin-by-category")
@login_required
def api_profit_margin_by_category():
    filters = _parse_filters()
    return jsonify(get_profit_margin_by_category(filters))


@app.route("/api/scatter-data")
@login_required
def api_scatter_data():
    filters = _parse_filters()
    return jsonify(get_scatter_data(filters))


@app.route("/api/radar-data")
@login_required
def api_radar_data():
    filters = _parse_filters()
    return jsonify(get_radar_data(filters))


@app.route("/api/year-over-year")
@login_required
def api_year_over_year():
    filters = _parse_filters()
    return jsonify(get_year_over_year(filters))


@app.route("/api/forecast")
@login_required
def api_forecast():
    filters = _parse_filters()
    months = request.args.get("months", 6, type=int)
    metric = request.args.get("metric", "all")
    result = {}
    if metric in ("all", "sales"):
        result["sales"] = forecast_sales(filters, months)
    if metric in ("all", "profit"):
        result["profit"] = forecast_profit(filters, months)
    if metric in ("all", "customers"):
        result["customers"] = forecast_customers(filters, months)
    return jsonify(result)


@app.route("/api/legacy-forecast")
@login_required
def api_legacy_forecast():
    filters = _parse_filters()
    months = request.args.get("months", 6, type=int)
    return jsonify(get_forecast(filters, months))


@app.route("/api/drilldown")
@login_required
def api_drilldown():
    filters = _parse_filters()
    level = request.args.get("level", "categories")
    parent = request.args.get("parent")
    return jsonify(get_drilldown(level, filters, parent))


@app.route("/api/insights")
@login_required
def api_insights():
    filters = _parse_filters()
    return jsonify(get_full_insights(filters))


@app.route("/api/executive-summary")
@login_required
def api_executive_summary():
    filters = _parse_filters()
    return jsonify(get_executive_summary(filters))


@app.route("/api/filter-options")
@login_required
def api_filter_options():
    return jsonify(get_filter_options())


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400
    filters = _parse_filters()
    result = process_query(question, filters)
    user_id = session.get("user_id")
    if user_id:
        log_activity(user_id, "chat", f"Asked: {question[:100]}")
    return jsonify(result)


@app.route("/api/what-if", methods=["POST"])
@login_required
def api_what_if():
    data = request.get_json() or {}
    discount_change = data.get("discount_change", 0)
    price_change = data.get("price_change", 0)
    volume_change = data.get("volume_change", 0)
    filters = _parse_filters()
    kpis = get_kpis(filters)
    current_sales = safe_float(kpis.get("total_sales", 0))
    current_profit = safe_float(kpis.get("total_profit", 0))
    current_orders = safe_float(kpis.get("total_orders", 0))
    new_sales = current_sales * (1 + price_change / 100) * (1 + volume_change / 100)
    discount_impact = discount_change * 0.5
    new_profit = new_sales * (1 - discount_impact / 100) - (current_sales * safe_float(kpis.get("profit_margin", 10)) / 100 * (1 - new_sales / current_sales if current_sales > 0 else 1))
    new_profit = new_sales * ((safe_float(kpis.get("profit_margin", 10)) / 100) + (price_change / 100) - (discount_change / 100 * 0.3))
    new_orders = current_orders * (1 + volume_change / 100)
    return jsonify({
        "current": {
            "sales": round(current_sales, 2),
            "profit": round(current_profit, 2),
            "orders": int(current_orders),
            "margin": round(safe_float(kpis.get("profit_margin", 0)), 2),
        },
        "projected": {
            "sales": round(new_sales, 2),
            "profit": round(new_profit, 2),
            "orders": int(new_orders),
            "margin": round((new_profit / new_sales * 100) if new_sales > 0 else 0, 2),
        },
        "changes": {
            "sales_change": round(new_sales - current_sales, 2),
            "profit_change": round(new_profit - current_profit, 2),
            "orders_change": int(new_orders - current_orders),
        },
        "assumptions": {
            "discount_change": discount_change,
            "price_change": price_change,
            "volume_change": volume_change,
        },
    })


@app.route("/api/customer-analytics", methods=["POST"])
@login_required
def api_customer_analytics():
    data = request.get_json() or {}
    analysis_type = data.get("type", "rfm")
    filters = _parse_filters()
    customers = get_customer_analysis(filters)
    if analysis_type == "rfm":
        return jsonify(_compute_rfm(customers))
    elif analysis_type == "clv":
        return jsonify(_compute_clv(customers))
    elif analysis_type == "churn":
        return jsonify(_compute_churn_risk(customers))
    elif analysis_type == "clusters":
        return jsonify(_compute_kmeans(customers))
    return jsonify({"error": "Invalid analysis type"}), 400


@app.route("/api/analytics-data")
@login_required
def api_analytics_data():
    filters = _parse_filters()
    return jsonify({
        "profit_margin": get_profit_margin_by_category(filters),
        "discount_analysis": get_discount_impact(filters),
        "shipping_performance": get_shipping_analysis(filters),
        "yoy_comparison": get_year_over_year(filters),
        "top_products": get_top_products(filters, 10),
        "bottom_products": get_bottom_products(filters, 10),
        "sub_category_breakdown": get_sub_category_sales(filters),
    })


@app.route("/api/customers-data")
@login_required
def api_customers_data():
    filters = _parse_filters()
    customers = get_customer_analysis(filters)
    seg_map = {}
    for c in customers:
        seg = c.get("segment", "Unknown")
        seg_map[seg] = seg_map.get(seg, 0) + 1
    sorted_customers = sorted(customers, key=lambda x: safe_float(x.get("total_spent", 0)), reverse=True)
    top_labels = [(c.get("customer_name", "") or "")[:25] for c in sorted_customers[:15]]
    top_values = [safe_float(c.get("total_spent", 0)) for c in sorted_customers[:15]]
    return jsonify({
        "segment_distribution": {"labels": list(seg_map.keys()), "values": list(seg_map.values())},
        "top_customers": {"labels": top_labels, "values": top_values},
        "customer_analysis": customers,
    })


@app.route("/api/products-data")
@login_required
def api_products_data():
    filters = _parse_filters()
    top = get_top_products(filters, 30)
    subcat = get_sub_category_sales(filters)
    scatter = get_scatter_data(filters)
    cat_sales = get_category_sales(filters)
    return jsonify({
        "treemap": {
            "labels": [s.get("sub_category", "") for s in subcat],
            "sales": [safe_float(s.get("sales", 0)) for s in subcat],
            "profit": [safe_float(s.get("profit", 0)) for s in subcat],
        },
        "scatter": scatter,
        "category_breakdown": {
            "labels": [c.get("category", "") for c in cat_sales],
            "values": [safe_float(c.get("sales", 0)) for c in cat_sales],
        },
        "sub_category_performance": {
            "labels": [s.get("sub_category", "") for s in subcat[:15]],
            "values": [safe_float(s.get("sales", 0)) for s in subcat[:15]],
        },
        "rankings": top,
    })


@app.route("/api/profit-data")
@login_required
def api_profit_data():
    filters = _parse_filters()
    trend = get_sales_trend(filters)
    margin = get_profit_margin_by_category(filters)
    states = get_state_performance(filters)
    return jsonify({
        "profit_trend": {
            "labels": [t.get("month", "") for t in trend],
            "profit": [safe_float(t.get("profit", 0)) for t in trend],
            "sales": [safe_float(t.get("sales", 0)) for t in trend],
        },
        "profit_by_category": {
            "labels": [m.get("category", "") for m in margin],
            "values": [safe_float(m.get("profit", 0)) for m in margin],
        },
        "profit_heatmap": {
            "labels": [s.get("state", "") for s in states[:20]],
            "values": [safe_float(s.get("profit", 0)) for s in states[:20]],
        },
        "profit_details": states,
    })


@app.route("/api/regions-data")
@login_required
def api_regions_data():
    filters = _parse_filters()
    regions = get_region_sales(filters)
    states = get_state_performance(filters)
    return jsonify({
        "regional_sales": {
            "labels": [r.get("region", "") for r in regions],
            "values": [safe_float(r.get("sales", 0)) for r in regions],
        },
        "state_performance": {
            "labels": [s.get("state", "") for s in states[:20]],
            "values": [safe_float(s.get("profit", 0)) for s in states[:20]],
        },
        "region_details": regions,
        "region_cards": regions,
    })


def _parse_filters():
    return {k: v for k, v in {
        "year": request.args.get("year"),
        "month": request.args.get("month"),
        "category": request.args.get("category"),
        "region": request.args.get("region"),
        "segment": request.args.get("segment"),
        "state": request.args.get("state"),
        "ship_mode": request.args.get("ship_mode"),
        "quarter": request.args.get("quarter"),
        "date_from": request.args.get("date_from"),
        "date_to": request.args.get("date_to"),
    }.items() if v}


def _compute_rfm(customers):
    if not customers:
        return {"segments": [], "summary": {}}
    total_spent_values = [safe_float(c.get("total_spent", 0)) for c in customers]
    order_counts = [int(safe_float(c.get("order_count", 1))) for c in customers]
    max_spent = max(total_spent_values) if total_spent_values else 1
    max_orders = max(order_counts) if order_counts else 1
    segments = {"Champions": 0, "Loyal": 0, "Potential": 0, "At Risk": 0, "Lost": 0}
    for c in customers:
        spent = safe_float(c.get("total_spent", 0))
        orders = int(safe_float(c.get("order_count", 1)))
        r_score = (spent / max_spent * 5) if max_spent > 0 else 0
        f_score = (orders / max_orders * 5) if max_orders > 0 else 0
        avg = (r_score + f_score) / 2
        if avg >= 4:
            segments["Champions"] += 1
        elif avg >= 3:
            segments["Loyal"] += 1
        elif avg >= 2:
            segments["Potential"] += 1
        elif avg >= 1:
            segments["At Risk"] += 1
        else:
            segments["Lost"] += 1
    return {"segments": [{"name": k, "count": v} for k, v in segments.items()], "summary": {"total_customers": len(customers)}}


def _compute_clv(customers):
    if not customers:
        return {"customers": [], "avg_clv": 0}
    results = []
    for c in customers:
        total_spent = safe_float(c.get("total_spent", 0))
        orders = int(safe_float(c.get("order_count", 1)))
        clv = total_spent * (1 + orders * 0.1)
        results.append({"name": c.get("customer_name", ""), "segment": c.get("segment", ""),
                        "total_spent": round(total_spent, 2), "orders": orders, "clv": round(clv, 2)})
    results.sort(key=lambda x: x["clv"], reverse=True)
    avg_clv = sum(r["clv"] for r in results) / len(results) if results else 0
    return {"customers": results[:20], "avg_clv": round(avg_clv, 2)}


def _compute_churn_risk(customers):
    if not customers:
        return {"customers": [], "summary": {}}
    results = []
    for c in customers:
        orders = int(safe_float(c.get("order_count", 1)))
        spent = safe_float(c.get("total_spent", 0))
        if orders <= 1:
            risk = "High"
            score = 85
        elif orders <= 2 and spent < 5000:
            risk = "Medium"
            score = 55
        else:
            risk = "Low"
            score = 20
        results.append({"name": c.get("customer_name", ""), "segment": c.get("segment", ""),
                        "orders": orders, "total_spent": round(spent, 2), "risk": risk, "score": score})
    summary = {"high": sum(1 for r in results if r["risk"] == "High"),
               "medium": sum(1 for r in results if r["risk"] == "Medium"),
               "low": sum(1 for r in results if r["risk"] == "Low")}
    return {"customers": results[:20], "summary": summary}


def _compute_kmeans(customers):
    if not customers or len(customers) < 4:
        return {"clusters": [], "centers": []}
    import numpy as np
    X = np.array([[safe_float(c.get("total_spent", 0)), int(safe_float(c.get("order_count", 1)))]
                  for c in customers])
    from sklearn.cluster import KMeans
    n_clusters = min(4, len(customers))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_.tolist()
    clusters = []
    for i in range(n_clusters):
        members = [customers[j] for j in range(len(customers)) if labels[j] == i]
        clusters.append({"cluster_id": i, "count": len(members),
                         "avg_spent": round(float(np.mean([safe_float(m.get("total_spent", 0)) for m in members])), 2),
                         "avg_orders": round(float(np.mean([safe_float(m.get("order_count", 1)) for m in members])), 1),
                         "sample_names": [m.get("customer_name", "") for m in members[:3]]})
    return {"clusters": clusters, "centers": [[round(c[0], 2), round(c[1], 2)] for c in centers]}


@app.route("/api/notifications")
@login_required
def api_notifications():
    user_id = session.get("user_id")
    unread_only = request.args.get("unread", "false") == "true"
    return jsonify(get_notifications(user_id, unread_only))


@app.route("/api/notifications/unread-count")
@login_required
def api_notifications_unread_count():
    user_id = session.get("user_id")
    return jsonify({"count": get_unread_count(user_id)})


@app.route("/api/notifications/read/<int:nid>", methods=["POST"])
@login_required
def api_notification_read(nid):
    mark_read(nid)
    return jsonify({"success": True})


@app.route("/api/notifications/read-all", methods=["POST"])
@login_required
def api_notification_read_all():
    mark_all_read(session.get("user_id"))
    return jsonify({"success": True})


@app.route("/api/users", methods=["GET"])
@login_required
@admin_required
def api_users():
    return jsonify(get_all_users())


@app.route("/api/users", methods=["POST"])
@login_required
@admin_required
def api_create_user():
    data = request.get_json() or {}
    user = create_user(data.get("username", ""), data.get("password", ""),
                       data.get("full_name", ""), data.get("email", ""), data.get("role", "analyst"))
    if user:
        log_audit(session.get("user_id"), "create_user", "users", f"Created user {user['username']}", request.remote_addr)
        return jsonify(user), 201
    return jsonify({"error": "Username already exists or invalid data"}), 400


@app.route("/api/users/<int:uid>", methods=["PUT"])
@login_required
@admin_required
def api_update_user(uid):
    data = request.get_json() or {}
    if update_user(uid, **data):
        log_audit(session.get("user_id"), "update_user", "users", f"Updated user {uid}", request.remote_addr)
        return jsonify({"success": True})
    return jsonify({"error": "Update failed"}), 400


@app.route("/api/users/<int:uid>", methods=["DELETE"])
@login_required
@admin_required
def api_delete_user(uid):
    if delete_user(uid):
        log_audit(session.get("user_id"), "delete_user", "users", f"Deleted user {uid}", request.remote_addr)
        return jsonify({"success": True})
    return jsonify({"error": "Delete failed"}), 400


@app.route("/api/audit-logs")
@login_required
@admin_required
def api_audit_logs():
    limit = request.args.get("limit", 50, type=int)
    return jsonify(get_audit_logs(limit))


@app.route("/api/activity-log")
@login_required
def api_activity_log():
    return jsonify(get_activity_log(20))


@app.route("/api/upload", methods=["POST"])
@login_required
@role_required("admin", "analyst")
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    upload_dir = app.config.get("UPLOAD_FOLDER", "uploads")
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)
    result = import_to_database(filepath, session.get("user_id"))
    if result["success"]:
        log_audit(session.get("user_id"), "upload_file", "uploads",
                  f"Uploaded {file.filename} ({result['records']} records)", request.remote_addr)
        log_activity(session.get("user_id"), "upload", f"Uploaded {file.filename}")
        create_notification(session.get("user_id"), "Upload Complete",
                           f"Successfully imported {result['records']} records from {file.filename}", "success")
    return jsonify(result)


@app.route("/api/data-profile")
@login_required
def api_data_profile():
    return jsonify(get_data_profile())


@app.route("/api/export/excel")
@login_required
def api_export_excel():
    filters = _parse_filters()
    filepath = generate_excel_report(filters)
    if filepath and os.path.exists(filepath):
        log_activity(session.get("user_id"), "export", "Exported Excel report")
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    return jsonify({"error": "Export failed"}), 500


@app.route("/api/export/csv")
@login_required
def api_export_csv():
    filters = _parse_filters()
    filepath = generate_csv_export(filters)
    if filepath and os.path.exists(filepath):
        log_activity(session.get("user_id"), "export", "Exported CSV report")
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    return jsonify({"error": "Export failed"}), 500


@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})
    like_q = f"%{q}%"
    results = []
    products = query_db(
        "SELECT product_name, category, ROUND(SUM(sales),2) as sales "
        "FROM sales WHERE product_name LIKE ? GROUP BY product_name ORDER BY sales DESC LIMIT 10",
        (like_q,)
    )
    for p in products:
        results.append({"type": "product", "name": p["product_name"],
                        "detail": f"{p['category']} - \u20B9{p['sales']:,.2f}", "icon": "fa-box"})
    states = query_db(
        "SELECT state, ROUND(SUM(sales),2) as sales, COUNT(DISTINCT order_id) as orders "
        "FROM sales WHERE state LIKE ? GROUP BY state ORDER BY sales DESC LIMIT 5",
        (like_q,)
    )
    for s in states:
        results.append({"type": "state", "name": s["state"],
                        "detail": f"{s['orders']} orders - \u20B9{s['sales']:,.2f}", "icon": "fa-map-marker-alt"})
    customers = query_db(
        "SELECT customer_name, segment, ROUND(SUM(sales),2) as total_spent "
        "FROM sales WHERE customer_name LIKE ? GROUP BY customer_id ORDER BY total_spent DESC LIMIT 5",
        (like_q,)
    )
    for c in customers:
        results.append({"type": "customer", "name": c["customer_name"],
                        "detail": f"{c['segment']} - \u20B9{c['total_spent']:,.2f}", "icon": "fa-user"})
    return jsonify({"results": results})


@app.route("/api/bookmarks", methods=["GET"])
@login_required
def api_get_bookmarks():
    user_id = session.get("user_id")
    bookmarks = query_db(
        "SELECT * FROM bookmarks WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    )
    return jsonify(bookmarks)


@app.route("/api/bookmarks", methods=["POST"])
@login_required
def api_save_bookmark():
    data = request.get_json() or {}
    user_id = session.get("user_id")
    execute_db("INSERT INTO bookmarks (user_id, page, filters_json, name) VALUES (?, ?, ?, ?)",
               (user_id, data.get("page", ""), data.get("filters", ""), data.get("name", "Untitled")))
    return jsonify({"success": True})


@app.route("/api/bookmarks/<int:bid>", methods=["DELETE"])
@login_required
def api_delete_bookmark(bid):
    execute_db("DELETE FROM bookmarks WHERE id = ? AND user_id = ?", (bid, session.get("user_id")))
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
