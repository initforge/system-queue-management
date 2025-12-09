import bcrypt

# Create hashes for different users
passwords = {
    "Staff@123": "staff",
    "Manager@123": "manager",
    "Admin123!": "admin"
}

for password, role in passwords.items():
    # Use bcrypt directly
    salt = bcrypt.gensalt()
    hash_value = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"Password hash for {role} ('{password}'): {hash_value.decode('utf-8')}")