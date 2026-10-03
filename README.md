# Superstore Business Analytics Dashboard

A premium Business Intelligence dashboard built with Python Flask, SQLite, and modern web technologies. Features AI-powered insights, 6-month forecasting, drill-down analysis, 4 dashboard themes, and drag-and-drop widget customization.

## Features

### Core Analytics
- **Interactive Dashboard** with animated KPI cards, trend indicators, and period-over-period comparisons
- **6-Month Forecasting** using linear regression for Sales and Profit
- **AI Business Insights Engine** with 13+ auto-generated, plain-English insights sorted by severity
- **3-Level Drill-Down**: Category -> Sub-Category -> Product with breadcrumb navigation
- **14+ Interactive Charts** using Chart.js (line, bar, doughnut, pie, scatter, radar, area)
- **Advanced Data Tables** with search, sort, pagination, and CSV export

### Dashboard Customization
- **4 Themes**: Light, Dark, Blue, Emerald with one-click switching
- **Drag-and-Drop Widgets** to rearrange chart positions (order saved to localStorage)
- **Filter System** with real-time auto-update: year, quarter, month, category, region, segment, ship mode
- **Interactive Breadcrumbs** showing active filter context
- **URL Sync** - filter state preserved in URL parameters

### Performance & Quality
- **API Response Caching** with 30s TTL to minimize redundant requests
- **53 Unit Tests** covering filters, analytics, routes, API endpoints, and error handling
- **Error Handling** on all API endpoints with proper HTTP status codes
- **Responsive Design** for desktop, laptop, tablet, and mobile

### UI/UX
- **Glassmorphism Navbar** with backdrop blur
- **Animated Hero Section** with floating shapes and dashboard preview
- **Micro-interactions**: hover lifts, icon scaling, gradient shifts, smooth transitions
- **Skeleton Loading** shimmer effect
- **Custom Scrollbar** styling
- **Print-optimized** styles

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python Flask 3.0                    |
| Database   | SQLite (auto-initialized from CSV)  |
| Frontend   | HTML5, CSS3, Bootstrap 5.3          |
| Charts     | Chart.js 4.x                       |
| Tables     | DataTables.js 1.13                  |
| Icons      | Font Awesome 6.5                    |
| Fonts      | Google Fonts (Poppins)             |
| Testing    | pytest 9.x                         |

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

1. Clone or download the project
   ```bash
   git clone <repository-url>
   cd Superstore-Business-Analytics
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   python app.py
   ```

4. Open in browser
   ```
   http://localhost:5000
   ```

5. Login with demo credentials
   ```
   Username: admin
   Password: admin123
   ```

6. Run tests
   ```bash
   python -m pytest test_app.py -v
   ```

## Project Structure

```
Superstore-Business-Analytics/
├── app.py                     # Flask application factory
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── database.db                # SQLite (auto-created on first run)
├── test_app.py                # 53 unit tests
├── dataset/
│   └── Superstore.csv         # Source data (100 records)
├── models/
│   ├── __init__.py
│   └── database.py            # DB init, CSV import, query helpers
├── routes/
│   ├── __init__.py
│   ├── api.py                 # 11 REST API endpoints
│   └── dashboard.py           # 9 page routes with auth
├── utils/
│   ├── __init__.py
│   └── analytics.py           # Analytics engine, forecasting, AI insights, drill-down
├── templates/
│   ├── index.html             # Landing page with hero section
│   ├── login.html             # Glassmorphism login
│   ├── dashboard.html         # Main dashboard with themes, drill-down, drag-drop
│   ├── analytics.html         # YoY comparison, margins
│   ├── products.html          # Product rankings, scatter plot
│   ├── customers.html         # Customer segmentation
│   ├── regions.html           # Regional analysis
│   ├── profit.html            # Profit analysis, discount impact
│   └── insights.html          # Auto-generated business insights
└── static/
    ├── css/
    │   ├── style.css          # Main styles with 4 theme definitions
    │   └── dashboard.css      # Dashboard layout, widgets, animations
    └── js/
        ├── charts.js          # Chart.js rendering, forecasting overlay
        ├── dashboard.js       # Main controller: themes, drag-drop, drill-down, caching
        ├── filters.js         # Filter panel with auto-update and URL sync
        └── table.js           # DataTable management and CSV export
```

## API Endpoints

| Endpoint           | Description                          |
|--------------------|--------------------------------------|
| `/api/dashboard`   | Dashboard data with KPIs, forecast   |
| `/api/sales`       | Monthly sales trend                  |
| `/api/products`    | Product analysis (top/bottom)        |
| `/api/customers`   | Customer segmentation data           |
| `/api/profit`      | Profit margins, discount impact      |
| `/api/regions`     | Regional and state performance       |
| `/api/analytics`   | Insights, YoY, forecast              |
| `/api/insights`    | AI-generated business insights       |
| `/api/filters`     | Available filter options             |
| `/api/forecast`    | Sales/profit forecast (configurable) |
| `/api/drilldown`   | Category -> Sub-category -> Product  |

All endpoints accept query parameters: `year`, `quarter`, `month`, `category`, `region`, `segment`, `ship_mode`.

## Analytics Engine

### Forecasting
Uses simple linear regression (`y = mx + b`) on monthly sales/profit data:
- Calculates slope, intercept, and R-squared
- Projects 6 months ahead
- Confidence metric based on R-squared

### AI Insights
Automatically generates insights analyzing:
- Revenue summary and period-over-period comparison
- Category performance and loss warnings
- Regional leaders and underperformers
- Segment analysis
- Trend detection (upward/downward)
- Forecast projections
- Customer value metrics
- Discount policy warnings

Each insight has a severity level: `critical`, `high`, `medium`, `low`.

### Drill-Down
Three-level hierarchical analysis:
1. **Categories** (3 items) with child counts
2. **Sub-Categories** filtered by parent category
3. **Products** filtered by parent sub-category

## Dashboard Themes

| Theme    | Primary Color | Sidebar    | Background |
|----------|---------------|------------|------------|
| Light    | #2563EB       | #0F172A    | #F8FAFC    |
| Dark     | #2563EB       | #060D19    | #0B1121    |
| Blue     | #3B82F6       | #1E3A5F    | #EFF6FF    |
| Emerald  | #059669       | #064E3B    | #ECFDF5    |

## Testing

53 unit tests covering:
- **TestFilterBuilder** (7 tests): SQL filter generation
- **TestAnalyticsFunctions** (14 tests): KPIs, forecasting, drill-down, insights
- **TestPageRoutes** (13 tests): All page routes and authentication
- **TestAPIRoutes** (17 tests): All API endpoints including filtered calls
- **TestAPIErrors** (2 tests): 404 and error handling

```bash
python -m pytest test_app.py -v
```

## Future Improvements

- [ ] PDF export with jsPDF
- [ ] Real-time data updates with WebSockets
- [ ] Geographic map visualization with Leaflet
- [ ] User role management and multi-user support
- [ ] Email report scheduling
- [ ] Custom dashboard builder with widget marketplace
- [ ] Data drill-down into individual transactions
- [ ] Anomaly detection with statistical methods
