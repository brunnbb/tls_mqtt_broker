from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import Name, NameAttribute, CertificateBuilder
from cryptography.x509.oid import NameOID
import datetime

# This module signs a csr to generate a crt that a client will be using 

def load_public_key(path: str):
    with open(path, "rb") as f:
        chave_publica_pem = f.read()
    return serialization.load_pem_public_key(chave_publica_pem)

def load_private_key(path: str):
    with open(path, "rb") as f:
        chave_privada_pem = f.read()
    return serialization.load_pem_private_key(chave_privada_pem, password=None)

def gerar_certificado_assinado(chave_privada_servidor, chave_publica_cliente, caminho_certificado_saida):
    # Informações do certificado
    subject = issuer = Name([
        NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
        NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"SC"),
        NameAttribute(NameOID.LOCALITY_NAME, u"Lages"),
        NameAttribute(NameOID.ORGANIZATION_NAME, u"IFSC"),
        NameAttribute(NameOID.COMMON_NAME, u"client4"),
    ])
    
    # Construir o certificado
    certificado = CertificateBuilder(
        subject_name=subject,
        issuer_name=issuer,
        public_key=chave_publica_cliente,
        serial_number=1000,
        not_valid_before=datetime.datetime.now(datetime.timezone.utc),
        not_valid_after=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).sign(private_key=chave_privada_servidor, algorithm=hashes.SHA256())

    # Salvar o certificado em formato .crt
    with open(caminho_certificado_saida, "wb") as f:
        f.write(certificado.public_bytes(serialization.Encoding.PEM))
    print(f"Certificado gerado e salvo em {caminho_certificado_saida}")

if __name__ == '__main__':
    caminho_chave_privada_servidor = r"src\security\server_keys\broker_priv_key.pem"
    caminho_chave_publica_cliente = r"src\security\client_keys\public_key_4.pem"
    caminho_certificado_saida = r"src\security\certificates\client4.crt"

    chave_privada_servidor = load_private_key(caminho_chave_privada_servidor)
    chave_publica_cliente = load_public_key(caminho_chave_publica_cliente)
    gerar_certificado_assinado(chave_privada_servidor, chave_publica_cliente, caminho_certificado_saida)