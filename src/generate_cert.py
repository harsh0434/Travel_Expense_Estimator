import os
import subprocess
from datetime import datetime, timedelta

def generate_certificates():
    try:
        # Create certificates directory if it doesn't exist
        cert_dir = 'certificates'
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)

        # Generate private key
        private_key_path = os.path.join(cert_dir, 'private.key')
        subprocess.run([
            'openssl', 'genrsa',
            '-out', private_key_path,
            '2048'
        ], check=True)

        # Generate CSR (Certificate Signing Request)
        csr_path = os.path.join(cert_dir, 'request.csr')
        subprocess.run([
            'openssl', 'req',
            '-new',
            '-key', private_key_path,
            '-out', csr_path,
            '-subj', '/CN=localhost'
        ], check=True)

        # Generate self-signed certificate
        cert_path = os.path.join(cert_dir, 'certificate.crt')
        subprocess.run([
            'openssl', 'x509',
            '-req',
            '-days', '365',
            '-in', csr_path,
            '-signkey', private_key_path,
            '-out', cert_path
        ], check=True)

        print("SSL certificates generated successfully!")
        print(f"Private key: {private_key_path}")
        print(f"Certificate: {cert_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    generate_certificates() 