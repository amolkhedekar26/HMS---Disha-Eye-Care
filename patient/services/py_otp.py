import pyotp


class TOTP:
    @staticmethod
    def generate_TOTP():
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=300)
        return {'secret': secret, 'otp': totp.now()}

    @staticmethod
    def verify_TOTP(secret, otp):
        totp = pyotp.TOTP(secret, interval=300)
        return totp.verify(otp)
