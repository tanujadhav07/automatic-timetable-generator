
#!/usr/bin/env bash
set -euo pipefail
cd frontend
npm ci
npm run build
cd ..
# After build, the Flask app will serve frontend/dist automatically
echo "Frontend built into frontend/dist"