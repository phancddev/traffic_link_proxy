import os
import requests
from time import sleep
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

def download_file(url, local_filename):
    # Tải về file từ URL và lưu vào một file cục bộ
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def get_proxies_from_links_file(filename):
    # Đọc các URL từ file, tải về file từ mỗi URL và thu thập tất cả các proxy từ các file đó
    proxies = []
    with open(filename, "r") as f:
        links = [line.strip() for line in f.readlines()]
        for link in links:
            parsed_link = urlparse(link)
            local_filename = os.path.join("/tmp", os.path.basename(parsed_link.path))
            download_file(link, local_filename)
            proxies.extend(get_proxies(local_filename))
    return proxies

def main():
    url = [input("Nhập vào link bạn muốn click: ") for _ in range(int(input("Nhập số lượng link: ")))]
    num_threads = int(input("Nhập số lượng luồng tối đa: "))
    
    if input("Bạn có muốn nhập file chứa link có proxy không? (y/n) ").lower() == "y":
        filename_http_links = input("Nhập vào tên tệp chứa link http proxy: ")
        filename_socks4_links = input("Nhập vào tên tệp chứa link socks4 proxy: ")
        filename_socks5_links = input("Nhập vào tên tệp chứa link socks5 proxy: ")
        proxies_http = get_proxies_from_links_file(filename_http_links)
        proxies_socks4 = get_proxies_from_links_file(filename_socks4_links)
        proxies_socks5 = get_proxies_from_links_file(filename_socks5_links)
    else:
        filename_http = input("Nhập vào tên tệp chứa http proxy: ")
        filename_socks4 = input("Nhập vào tên tệp chứa socks4 proxy: ")
        filename_socks5 = input("Nhập vào tên tệp chứa socks5 proxy: ")
        proxies_http = get_proxies(filename_http)
        proxies_socks4 = get_proxies(filename_socks4)
        proxies_socks5 = get_proxies(filename_socks5)

    successful_requests = 0
    used_proxies = []

    # Tiếp tục như phần còn lại của hàm main...

if __name__ == "__main__":
    main()
 
# Sử dụng ThreadPoolExecutor để gửi nhiều yêu cầu cùng một lúc
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for proxy_type, proxies in enumerate([proxies_http, proxies_socks4, proxies_socks5]):
            for proxy in proxies:
                if proxy_type == 0:  # http proxy
                    futures = [executor.submit(send_request_http, u, proxy) for u in url]
                elif proxy_type == 1:  # socks4 proxy
                    futures = [executor.submit(send_request_socks4, u, proxy) for u in url]
                else:  # socks5 proxy
                    futures = [executor.submit(send_request_socks5, u, proxy) for u in url]
                for future in futures:
                    if future.result():
                        successful_requests += 1
                used_proxies.append(proxy)
                print(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
                sleep(1)  # Delay giữa các request để tránh bị block
        proxies_http = [p for p in proxies_http if p not in used_proxies]
        proxies_socks4 = [p for p in proxies_socks4 if p not in used_proxies]
        proxies_socks5 = [p for p in proxies_socks5 if p not in used_proxies]

    save_unused_proxies(filename_http, proxies_http)
    save_unused_proxies(filename_socks4, proxies_socks4)
    save_unused_proxies(filename_socks5, proxies_socks5)

if __name__ == "__main__":
    main()