from werkzeug.security import generate_password_hash, check_password_hash


hashed_password = generate_password_hash('', method='pbkdf2:sha256')
print(hashed_password)

print(check_password_hash(hashed_password, ''))
