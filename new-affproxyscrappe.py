import requests
from fake_useragent import UserAgent
import time
def click_affiliate_link(url, proxy):
    headers = {
        'User-Agent': UserAgent().random,
        'Referer': 'https://soichieu.me/',
        'Connection': 'keep-alive',
        'Cookie': 'cookie_name=cookie_value; another_cookie=another_value'  # Thay đổi giá trị này để giả mạo cookies
        # Thêm các headers cần thiết khác nếu cần
    }

    try:
        response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

if __name__ == "__main__":
    aff_link = input("Nhập link aff: ")

    success_count = 0
    total_requests = 0

    with open('proxies.txt', 'r') as file:
        proxies = file.read().splitlines()

    delay_time = int(input("Nhập thời gian chờ giữa các requests (giây): "))

    cookies_to_use = {
        'cookie_name': 'cookie_value',
        'another_cookie': 'another_value'
        # Thêm các cookies cần giả mạo vào đây
    }

    cookie_str = '; '.join([f'{key}={value}' for key, value in cookies_to_use.items()])

    for proxy in proxies:
        result = click_affiliate_link(aff_link, proxy)
        total_requests += 1
        if result:
            success_count += 1
            print(f"Request to {aff_link} using {proxy} successful")
        else:
            print(f"Request to {aff_link} using {proxy} failed")
        
        time.sleep(delay_time)

    print(f"Total requests made: {total_requests}")
    print(f"Successful requests: {success_count}")
