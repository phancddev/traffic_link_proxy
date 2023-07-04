import requests
from time import sleep
from concurrent.futures import ThreadPoolExecutor

# Hàm để gửi yêu cầu đến một URL sử dụng proxy
def send_request_socks4(url, proxy):
    proxies = {
        "http": "socks4://" + proxy,
        "https": "socks4://" + proxy
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        print(f"Request sent to {url} with proxy {proxy}")
        return True
    except Exception as e:
        print(f"Failed to send request with proxy {proxy}. Reason: {e}")
        return False

# Hàm để đọc tất cả các proxy từ một tệp
def get_proxies(filename):
    with open(filename, "r") as f:
        proxies = [line.strip() for line in f.readlines()]
    return proxies

# Hàm để ghi các proxy chưa sử dụng trở lại vào file
def save_unused_proxies(filename, proxies):
    with open(filename, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def main():
    url = input("Nhập vào link bạn muốn click: ")
    filename = input("Nhập vào tên tệp chứa proxy: ")
    num_threads = int(input("Nhập số lượng luồng tối đa: "))
    proxies = get_proxies(filename)
    
    successful_requests = 0
    used_proxies = []

    # Sử dụng ThreadPoolExecutor để gửi nhiều yêu cầu cùng một lúc
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request_socks4, url, proxy) for proxy in proxies]
        for future in futures:
            if future.result():
                successful_requests += 1
            used_proxies.append(proxies.pop(0))
            print(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
            sleep(1)  # Delay giữa các request để tránh bị block

    save_unused_proxies(filename, proxies)

if __name__ == "__main__":
    main()
