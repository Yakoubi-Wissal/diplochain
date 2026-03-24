import bcrypt

password = "Admin@1234"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"Fresh hash for 'Admin@1234': {hashed}")
