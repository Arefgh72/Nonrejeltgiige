# --- تغییر اصلی: استفاده از curl_cffi ---
from curl_cffi.requests import get
import base64
import os
import sys # برای چاپ خطا

# --- آدرس ثابت منبع پراکسی ---
SUBSCRIPTION_URL = "https://raw.githubusercontent.com/Arefgh72/v2ray-proxy-pars-tester/main/output/github_all.txt"
RAW_PROXIES_OUTPUT_PATH = 'all_proxies_raw.txt' # سازگار با برنامه Go

def log_error(source, message, details):
    """یک تابع ساده برای لاگ خطا در stderr."""
    print(f"ERROR [{source}]: {message} | Details: {details}", file=sys.stderr)

def fetch_and_decode_link(link: str) -> list[str]:
    """پراکسی‌ها را از یک لینک دریافت و دیکود می‌کند."""
    clean_link = link.split('#')[0].strip()
    try:
        print(f"Fetching: {clean_link[:80]}...")
        # --- تغییر اصلی: استفاده از impersonate برای تقلید از مرورگر کروم ---
        response = get(clean_link, timeout=30, impersonate="chrome110")
        response.raise_for_status()

        content = response.text
        proxies = []

        try:
            # تلاش برای دیکود کردن محتوای Base64
            decoded_content = base64.b64decode(content).decode('utf-8')
            proxies = decoded_content.splitlines()
            print(f"  -> Decoded as Base64.")
        except Exception:
            # اگر دیکود نشد، به عنوان متن ساده پردازش می‌شود
            proxies = content.splitlines()
            print(f"  -> Processed as Plain Text.")

        # --- فیلتر کردن پراکسی‌های معتبر ---
        VALID_PROTOCOLS = ('vmess://', 'vless://', 'trojan://', 'ss://', 'hy://', 'hysteria://', 'hy2://')
        valid_proxies = [p.strip() for p in proxies if p.strip().startswith(VALID_PROTOCOLS)]
        print(f"  -> Found {len(valid_proxies)} valid proxies.")
        return valid_proxies

    except Exception as e:
        log_error("Fetch Proxies (Network)", f"Failed to fetch from link: {clean_link}", str(e))
        return []

def main():
    print("--- Running 01_fetch_proxies.py (with Browser Impersonation) ---")

    # --- مستقیم پراکسی‌ها را از لینک ثابت دریافت می‌کند ---
    all_proxies = fetch_and_decode_link(SUBSCRIPTION_URL)

    # --- حذف پراکسی‌های تکراری ---
    unique_proxies = list(dict.fromkeys(all_proxies))
    print(f"\nTotal unique proxies fetched: {len(unique_proxies)}")

    # --- ذخیره پراکسی‌ها در فایل خروجی ---
    with open(RAW_PROXIES_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(unique_proxies))
    print(f"Successfully saved {len(unique_proxies)} proxies to '{RAW_PROXIES_OUTPUT_PATH}'.")
    print("--- Finished 01_fetch_proxies.py ---")

if __name__ == "__main__":
    main()
