#!/bin/bash
# Step 1: Check what tables exist
echo "=== Tables in diplochain_db ==="
docker exec diplochain_postgres psql -U diplochain_user -d diplochain_db -c "\dt public.*"

# Step 2: Apply the seed data
echo ""
echo "=== Applying seed_data.sql ==="
docker exec -i diplochain_postgres psql -U diplochain_user -d diplochain_db < /home/wissal/diplochain/backend/database/seed_data.sql

# Step 3: Update passwords to a known hash (Admin@1234)
echo ""
echo "=== Updating passwords ==="
docker exec diplochain_postgres psql -U diplochain_user -d diplochain_db -c "
UPDATE public.\"User\" 
SET password = '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
WHERE email IN ('admin@diplochain.tn', 'contact@esprit.tn', 'student1@esprit.tn');
"

# Step 4: Verify
echo ""
echo "=== Final User Table ==="
docker exec diplochain_postgres psql -U diplochain_user -d diplochain_db -c "SELECT id_user, email, status FROM public.\"User\";"
