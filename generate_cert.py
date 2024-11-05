from OpenSSL import crypto
from datetime import datetime, timedelta
import os

def generate_self_signed_cert(cert_file, key_file, days=365):
    # Cek apakah sertifikat sudah ada dan masih berlaku
    if os.path.isfile(cert_file):
        existing_cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert_file, 'rt').read())
        expiration_date = datetime.strptime(existing_cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')
        if datetime.now() < expiration_date:
            print("Certificate is still valid. No need to create a new one.")
            return

    # Buat sertifikat baru jika tidak ada atau sudah kadaluwarsa
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.get_subject().C = "ID"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "Organization"
    cert.get_subject().CN = "192.168.0.176"  # Ganti dengan IP atau nama domain yang sesuai
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(days * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_file, 'wt') as certfile:
        certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))

    with open(key_file, 'wt') as keyfile:
        keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8'))

    print("A new certificate has been created.")

if __name__ == "__main__":
    generate_self_signed_cert('cert.pem', 'key.pem')
