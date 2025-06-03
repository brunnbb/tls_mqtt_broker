from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

# === 1. Carregar o CSR recebido ===
with open(r"src\auth\certificates\meu_csr.csr", "rb") as f:
    csr = x509.load_pem_x509_csr(f.read(), default_backend())

# === 2. Gerar chave e certificado da CA (simulada) ===
# (Você pode salvar isso se quiser persistir)
ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ca_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Minha CA Teste"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Minha Root CA"),
])

ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_subject)
    .issuer_name(ca_subject)
    .public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 anos
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    )
    .sign(private_key=ca_key, algorithm=hashes.SHA256())
)

# === 3. Emitir certificado assinado para o CSR ===
cert = (
    x509.CertificateBuilder()
    .subject_name(csr.subject)
    .issuer_name(ca_cert.subject)
    .public_key(csr.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))  # 1 ano
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    )
    .sign(private_key=ca_key, algorithm=hashes.SHA256())
)

# === 4. Salvar o certificado assinado (.crt) ===
with open(r"src\auth\certificates\certificado_assinado.crt", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

# === (Opcional) Salvar o certificado da CA ===
with open(r"src\auth\certificates\ca_certificado.crt", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

# === (Opcional) Salvar chave privada da CA (para testes locais) ===
with open(r"src\auth\certificates\ca_privada.key", "wb") as f:
    f.write(ca_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

print("✅ Certificado assinado salvo como 'certificado_assinado.crt'")
