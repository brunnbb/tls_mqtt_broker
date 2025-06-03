from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

# 1. Gerar a chave privada
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# 2. Informações do certificado
name = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "São Paulo"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "São Paulo"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Minha Empresa Ltda"),
    x509.NameAttribute(NameOID.COMMON_NAME, "www.exemplo.com"),
])

# 3. Criar o CSR
csr = x509.CertificateSigningRequestBuilder().subject_name(
    name
).sign(key, hashes.SHA256())

# 4. Salvar chave privada em um arquivo
with open(r"src\auth\certificates\chave_privada.key", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 5. Salvar o CSR em um arquivo
with open(r"src\auth\certificates\meu_csr.csr", "wb") as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))
