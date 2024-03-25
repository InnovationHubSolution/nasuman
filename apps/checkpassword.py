from werkzeug.security import generate_password_hash, check_password_hash

# Plain-text password to be hashed
plain_password = "tanna"

# Hash the plain-text password
hashed_password = generate_password_hash(plain_password)

print("Plain-text password:", plain_password)
print("Hashed password:", hashed_password)

# Simulate a login attempt with a provided password
provided_password = "tanna"

# Check if the provided password matches the hashed password
if check_password_hash(hashed_password, provided_password):
    print("Password is correct!")
else:
    print("Password is incorrect!")

