"""Debug 404 errors by checking all referenced URLs in templates."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app

# Collect all url_for references from templates
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

with app.test_client() as c:
    c.post('/login', data={'username': 'admin', 'password': 'admin123'})
    
    # Check all page routes
    pages = ['/', '/dashboard', '/analytics', '/products', '/customers', '/regions',
             '/profit', '/insights', '/forecasting', '/what-if', '/customer-analytics',
             '/chatbot', '/upload', '/reports', '/builder', '/search', '/admin', '/settings']
    
    for page in pages:
        r = c.get(page)
        status = 'OK' if r.status_code == 200 else f'FAIL ({r.status_code})'
        print(f'{status}: GET {page}')
    
    # Check all API endpoints
    apis = [
        '/api/dashboard-data', '/api/kpis', '/api/kpi-comparisons',
        '/api/sales-trend', '/api/category-sales', '/api/region-sales',
        '/api/segment-analysis', '/api/top-products', '/api/bottom-products',
        '/api/state-performance', '/api/shipping-analysis', '/api/discount-impact',
        '/api/sub-category-sales', '/api/customer-analysis',
        '/api/profit-margin-by-category', '/api/scatter-data', '/api/radar-data',
        '/api/year-over-year', '/api/forecast', '/api/forecast?metric=sales&months=6',
        '/api/legacy-forecast', '/api/drilldown', '/api/insights',
        '/api/executive-summary', '/api/filter-options',
        '/api/activity-log', '/api/data-profile', '/api/search?q=test',
        '/api/bookmarks', '/api/notifications',
    ]
    
    for api in apis:
        r = c.get(api)
        status = 'OK' if r.status_code == 200 else f'FAIL ({r.status_code})'
        print(f'{status}: GET {api}')
    
    # Check POST APIs
    r = c.post('/api/what-if', json={'discount_change': 10, 'price_change': 5, 'volume_change': 10})
    print(f'{"OK" if r.status_code == 200 else "FAIL ("+str(r.status_code)+")"}: POST /api/what-if')
    
    r = c.post('/api/chat', json={'question': 'total sales'})
    print(f'{"OK" if r.status_code == 200 else "FAIL ("+str(r.status_code)+")"}: POST /api/chat')
    
    r = c.post('/api/customer-analytics', json={'type': 'rfm'})
    print(f'{"OK" if r.status_code == 200 else "FAIL ("+str(r.status_code)+")"}: POST /api/customer-analytics')
    
    r = c.post('/api/notifications/read-all')
    print(f'{"OK" if r.status_code == 200 else "FAIL ("+str(r.status_code)+")"}: POST /api/notifications/read-all')
    
    # Check static files
    statics = [
        '/static/css/style.css', '/static/css/dashboard.css',
        '/static/js/app.js', '/static/js/charts.js', '/static/js/filters.js',
        '/static/js/table.js', '/static/js/dashboard.js',
    ]
    for s in statics:
        r = c.get(s)
        status = 'OK' if r.status_code == 200 else f'FAIL ({r.status_code})'
        print(f'{status}: GET {s}')
