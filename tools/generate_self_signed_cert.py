#!/usr/bin/env python3
"""
Gera um certificado TLS autoassinado para uso local.
Gera `certs/cert.pem` e `certs/key.pem`.
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
import ipaddress
import os

CERT_DIR = os.path.join(os.path.dirname(__file__), "..", "certs")
CERT_FILE = os.path.join(CERT_DIR, "cert.pem")
KEY_FILE = os.path.join(CERT_DIR, "key.pem")

os.makedirs(CERT_DIR, exist_ok=True)

# Se já existe, não sobrescrever
if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
    print("Certificado já existe em:", CERT_FILE)
    print("Usando certificados existentes.")
else:
    # Gerar chave privada
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    # Construir subject / issuer
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sao Paulo"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Adapta MCP"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    issuer = subject

    # Validity
    now = datetime.datetime.utcnow()
    cert_builder = x509.CertificateBuilder()
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(issuer)
    cert_builder = cert_builder.public_key(key.public_key())
    cert_builder = cert_builder.serial_number(x509.random_serial_number())
    cert_builder = cert_builder.not_valid_before(now - datetime.timedelta(days=1))
    cert_builder = cert_builder.not_valid_after(now + datetime.timedelta(days=3650))

    # Subject Alternative Names (localhost and 127.0.0.1)
    san = x509.SubjectAlternativeName([
        x509.DNSName(u"localhost"),
        x509.DNSName(u"127.0.0.1"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ])
    cert_builder = cert_builder.add_extension(san, critical=False)

    # Usos de chave
    cert_builder = cert_builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True
    )

    # Assinar
    certificate = cert_builder.sign(private_key=key, algorithm=hashes.SHA256(), backend=default_backend())

    # Escrever arquivos
    with open(KEY_FILE, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(CERT_FILE, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    print("Gerado certificado autoassinado:")
    print("  Cert:", CERT_FILE)
    print("  Key:", KEY_FILE)
