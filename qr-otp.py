import qrcode
import base64
import os

# For example, generate a 32-byte key
key = os.urandom(32)

# Encode the key in Base32
base32_encoded_bytes = base64.b32encode(key)
base32_encoded_str = base32_encoded_bytes.decode('utf-8')
# Optionally remove padding (if needed by your TOTP app)
base32_encoded_str = base32_encoded_str.rstrip('=')

print("Base32 Encoded Key:", base32_encoded_str)

# Construct the provisioning URI manually.
# You can change 'MyApp' and 'user@example.com' as needed.
label = "Align AP6 APP"  # Or just "MyLabel" if you don't have both pieces
issuer = "Align"
uri = f"otpauth://totp/{label}?secret={base32_encoded_str }&issuer={issuer}"
print("Provisioning URI:", uri)

# Generate the QR Code from the URI
qr = qrcode.make(uri)

# Save the QR Code as an image file (e.g., totp_qr.png)
qr.save("totp_qr.png")


print("QR Code saved as totp_qr.png")

