import sys, os
sys.path.insert(0, os.getcwd())
from app.main import app
routes = [(r.path, sorted(r.methods)) for r in app.routes if hasattr(r, 'methods')]
for p, m in sorted(routes):
    print(m, p)
