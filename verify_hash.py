import bcrypt

password = "Admin@1234"
hash_to_check = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

if bcrypt.checkpw(password.encode('utf-8'), hash_to_check.encode('utf-8')):
    print("MATCH: Password is correct for this hash.")
else:
    print("NO MATCH: The hash does not match 'Admin@1234'.")
