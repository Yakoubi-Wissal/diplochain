#!/usr/bin/env python3
"""Fix admin login by updating DB password hash via Docker."""
import subprocess
import bcrypt

# Generate hash for Admin@1234
pw = "Admin@1234"
h = bcrypt.hashpw(pw.encode(), bcrypt.gensalt(12)).decode()
print(f"Hash: {h}")

# Escape single quotes for SQL
h_escaped = h.replace("'", "''")
sql = f"UPDATE public.\"User\" SET password='{h_escaped}' WHERE email IN ('admin@diplochain.tn', 'contact@esprit.tn', 'student1@esprit.tn'); SELECT id_user, email FROM public.\"User\";"

# Try via docker exec
result = subprocess.run(
    ["docker", "exec", "diplochain_postgres", "psql", "-U", "diplochain_user", "-d", "diplochain_db", "-c", sql],
    capture_output=True, text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Code:", result.returncode)
