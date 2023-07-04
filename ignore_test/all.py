import requests
from time import sleep
from concurrent.futures import ThreadPoolExecutor

# Hàm để gửi yêu cầu đến một URL sử dụng http proxy
def send_request_http(url, proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }
    return send_request(url, proxies, proxy)

# Hàm để gửi yêu cầu đến một URL sử dụng socks4 proxy
def send_request_socks4(url, proxy):
    proxies = {
        "http": "socks4://" + proxy,
        "https": "socks4://" + proxy
    }
    return send_request(url, proxies, proxy)

# Hàm để gửi yêu cầu đến một URL sử dụng socks5 proxy
def send_request_socks5(url, proxy):
    proxies = {
        "http": "socks5://" + proxy,
        "https": "socks5://" + proxy
    }
    return send_request(url, proxies, proxy)

# Hàm để gửi yêu cầu đến một URL
def send_request(url, proxies, proxy):
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
    filename_http = input("Nhập vào tên tệp chứa http proxy: ")
    filename_socks4 = input("Nhập vào tên tệp chứa socks4 proxy: ")
    filename_socks5 = input("Nhập vào tên tệp chứa socks5 proxy: ")
    num_threads = int(input("Nhập số lượng luồng tối đa: "))
    proxies_http = get_proxies(filename_http)
    proxies_socks4 = get_proxies(filename_socks4)
    proxies_socks5 = get_proxies(filename_socks5)
    
    successful_requests = 0
    used_proxies = []

    # Sử dụng ThreadPoolExecutor để gửi nhiều yêu cầu cùng một lúc
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures_http = [executor.submit(send_request_http, url, proxy) for proxy in proxies_http]
        futures_socks4 = [executor.submit(send_request_socks4, url, proxy) for proxy in proxies_socks4]
        futures_socks5 = [executor.submit(send_request_socks5, url, proxy) for proxy in proxies_socks5]
        futures = futures_http + futures_socks4 + futures_socks5
        for future in futures:
            if future.result():
                successful_requests += 1
            used_proxies.append(proxies_http.pop(0) if futures.index(future) < len(futures_http)
                                else proxies_socks4.pop(0) if futures.index(future) < len(futures_http) + len(futures_socks4)
                                else proxies_socks5.pop(0))
            print(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
            sleep(1)  # Delay giữa các request để tránh bị block

    save_unused_proxies(filename_http, proxies_http)
    save_unused_proxies(filename_socks4, proxies_socks4)
    save_unused_proxies(filename_socks5, proxies_socks5)

if __name__ == "__main__":
    main()
