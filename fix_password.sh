#!/bin/bash
# Fix admin password in DiploChain database
# This hash corresponds to password: Admin@1234
HASH='$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'

docker exec diplochain_postgres psql -U diplochain_user -d diplochain_db -c "
UPDATE public.\"User\" 
SET password = '$HASH'
WHERE email IN ('admin@diplochain.tn', 'contact@esprit.tn', 'student1@esprit.tn');
SELECT id_user, email, status FROM public.\"User\";
"
