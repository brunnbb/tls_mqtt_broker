from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Creates RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize private key to pem 
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # ou PKCS8
    encryption_algorithm=serialization.NoEncryption()
)

# Saving private key in a file
with open("private_key.pem", "wb") as f:
    f.write(private_pem)

# Extract public key from private key
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Saving public key in a file
with open("public_key.pem", "wb") as f:
    f.write(public_pem)

print("Keys created and saved")
