import bcrypt

passwords = {
    "Admin@1234": "admin@diplochain.tn",
    "Password123": "admin@diplochain.tn",
    "diplochain": "admin@diplochain.tn",
}

# Generate hashes for the desired passwords
target_passwords = ["Admin@1234", "Password123", "admin123", "diplochain"]
for pw in target_passwords:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pw.encode('utf-8'), salt).decode('utf-8')
    print(f"Password: '{pw}' -> Hash: {hashed}")

# Check if existing hash in seed_data.sql corresponds to anything
existing_hash = "$2b$12$LQv3c1yqBWVHxkd0LpafE.Kbh6.p5O5uYqx/fG9A03hK9z6B6a.iW"
for pw in ["password", "Password", "admin", "Admin@1234", "secret", "diplochain", "123456"]:
    result = bcrypt.checkpw(pw.encode('utf-8'), existing_hash.encode('utf-8'))
    if result:
        print(f"\nEXISTING HASH MATCHES: '{pw}'")
        break
else:
    print("\nExisting hash does NOT match any common password. Need to re-seed the DB.")
