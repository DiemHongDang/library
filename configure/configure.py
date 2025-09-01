import subprocess
import sys

REQUIRED_PACKAGES = [
    "bcrypt",
    "pillow",     # thay vì PIL
    "opencv-python",
    "pyzbar",
    "qrcode"
]

def install_missing():
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg if pkg != "pillow" else "PIL")
        except ImportError:
            print(f"[INFO] Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

if __name__ == "__main__":
    install_missing()
    print("✅ All required packages are installed.")
