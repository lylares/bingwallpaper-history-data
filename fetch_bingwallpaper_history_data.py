import os
import json
import time
import random
import requests
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# 公钥
PUBLIC_KEY_PEM = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvGkxb6fi4ZVCWQMaW7k1s8wqUltOPDE2R4N5XWOXDeDMfGDGKZSWTNs0QTPoXS96egM3GVJcY9Lmfxos/dDkeN3SD7811/vuIqNHX/fogIEC2o8mq2BVkxudfN0UkvT4+5HNd3e3kYQIFg5/Jmn+rMJ3oCvlJvjwNi+6+yo3rQYFPbVzWQz+RVocluRxpCKaOMOsihRhRKJWygL0h7vObClo1SnC6ij+CcbrEGwKyxNsxX5Ykb/BF7bHgN+hnn4fT2rO0uBQekbrRxxWZU5pZ+mnZwe4UrseReH86JY2ALHgJ+3CY57EgPAqDM9mqBdxZnHX/oIOXu2ZKYQEn68jbwIDAQAB
-----END PUBLIC KEY-----'''

def get_param(year, month):
    try:
        params = {
            "param1": str(int(time.time() * 1000)),
            "param2": f"{year}-{month:02d}"
        }
        # 保证和 JS 一致的 JSON 字符串
        json_str = json.dumps(params, separators=(',', ':'))
        public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM.encode(), backend=default_backend())
        encrypted = public_key.encrypt(json_str.encode(), padding.PKCS1v15())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"Error in get_param: {e}")
        raise

def wait_random(min_ms, max_ms):
    try:
        ms = min_ms + random.random() * (max_ms - min_ms)
        time.sleep(ms / 1000)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        raise
    except Exception as e:
        print(f"Error in wait_random: {e}")
        raise

def fetch_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            backoff = 2000 * (attempt + 1) + random.random() * 1000
            print(f"Fetch failed (attempt {attempt + 1}), retrying in {int(backoff)}ms...")
            time.sleep(backoff / 1000)

def fetch_data_for_date_range(start_year, start_month, end_year, end_month):
    url = "https://bing.xxxxx.com/bing/info/list"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    total_months = (end_year - start_year) * 12 + (end_month - start_month + 1)
    current_month = 0

    try:
        for year in range(start_year, end_year + 1):
            start_m = start_month if year == start_year else 1
            end_m = end_month if year == end_year else 12

            for month in range(start_m, end_m + 1):
                current_month += 1
                progress = (current_month / total_months) * 100
                print(f"\nProgress: {progress:.1f}% ({current_month}/{total_months})")
                print(f"Fetching data for {year}-{month:02d}")
                
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": get_param(year, month),
                        "User-Agent": user_agent
                    }
                    response = fetch_with_retry(url, headers)
                    print("Response text:", response.text)  # 调试用
                    data = response.json()

                    # 保存到 年份/月份/ 目录下
                    year_dir = str(year)
                    month_dir = os.path.join(year_dir, f"{month:02d}")
                    os.makedirs(month_dir, exist_ok=True)
                    file_path = os.path.join(month_dir, "data.json")
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)

                    print(f"Successfully saved data for {year}-{month:02d}")
                    
                    # 请求间隔 随机抖动
                    wait_random(3000, 5000)
                except Exception as e:
                    print(f"Error fetching data for {year}-{month}: {e}")
                    continue

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        raise
    except Exception as e:
        print(f"Error in fetch_data_for_date_range: {e}")
        raise

def main():
    start_year = 2018
    start_month = 1
    end_year = 2025
    end_month = 4

    print("Starting data fetch...")
    print(f"Date range: {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
    
    try:
        fetch_data_for_date_range(start_year, start_month, end_year, end_month)
        print("\nData fetch completed. All results saved by year/month/data.json")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError in main execution: {e}")

if __name__ == "__main__":
    main() 