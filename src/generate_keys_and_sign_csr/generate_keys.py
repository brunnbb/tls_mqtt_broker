from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Gerar chave privada RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serializar chave privada em PEM
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # ou PKCS8
    encryption_algorithm=serialization.NoEncryption()
)

# Salvar chave privada em arquivo
with open("private_key.pem", "wb") as f:
    f.write(private_pem)

# Derivar e serializar chave pública
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Salvar chave pública em arquivo
with open("public_key.pem", "wb") as f:
    f.write(public_pem)

print("Chaves geradas e salvas com sucesso.")
