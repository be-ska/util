import qrcode
from urllib.parse import quote

# Secret must be Base32 (that's the format TOTP apps expect).
secret = "C6NKJAHMIYYC4UJAJXBUWNXAWBPODQ35LKYLVMRC3FEZYHIHJBSQ"

print("Base32 Encoded Key:", secret)

# Construct the provisioning URI manually.
# You can change the label and issuer as needed.
label = "Align AP6 APP"
issuer = "Align"
uri = (
    f"otpauth://totp/{quote(issuer)}:{quote(label)}"
    f"?secret={secret}&issuer={quote(issuer)}"
)
print("Provisioning URI:", uri)

# Generate the QR Code from the URI
qr = qrcode.make(uri)

# Save the QR Code as an image file (e.g., totp_qr.png)
qr.save("totp_qr.png")

print("QR Code saved as totp_qr.png")
