# -*- coding: utf-8 -*-
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import init_db

# 1. Update app/main.py
main_file = BASE_DIR / "app" / "main.py"
main_text = main_file.read_text(encoding="utf-8")
main_text = main_text.replace("SET status = 'Completado', ultima_fecha = ?, updated_at = CURRENT_TIMESTAMP", "SET status = 'Completado', ultima_fecha = ?")
main_file.write_text(main_text, encoding="utf-8")
print("[OK] main.py updated")

# 2. Update app/database.py
db_file = BASE_DIR / "app" / "database.py"
db_text = db_file.read_text(encoding="utf-8")
if "'planes_preventivos'" not in db_text[db_text.find("for table in ["):db_text.find("for table in [") + 200]:
    db_text = db_text.replace("for table in ['solicitudes_mantenimiento',", "for table in ['planes_preventivos', 'solicitudes_mantenimiento',")
    db_file.write_text(db_text, encoding="utf-8")
    print("[OK] database.py updated")

# 3. Update tests/test_gmao_senior_rules.py
test_file = BASE_DIR / "tests" / "test_gmao_senior_rules.py"
test_text = test_file.read_text(encoding="utf-8")
test_text = test_text.replace(
    "compras_block_start = self.html_content.find(\"currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras'\")",
    "compras_block_start = self.html_content.rfind(\"currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras'\")"
)
test_file.write_text(test_text, encoding="utf-8")
print("[OK] test_gmao_senior_rules.py updated")

# 4. Migrate DB
init_db()
print("[OK] DB re-migrated")
