import os
import requests
import tempfile
import logging
from time import sleep
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_country_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data['status'] == "success":
            country_code = data['countryCode']
            country = data['country']
            return country_code, country
        return None, None
    except Exception as e:
        logging.error(f"Error checking IP: {e}")
        return None, None


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def get_proxies(filename):
    with open(filename, "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f.readlines()]
    return proxies


def get_proxies_from_links_file(filename):
    proxies = []
    with open(filename, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f.readlines()]
        for link in links:
            parsed_link = urlparse(link)
            basename = os.path.basename(parsed_link.path)
            if basename:
                local_filename = os.path.join(tempfile.gettempdir(), basename)
                try:
                    download_file(link, local_filename)
                    new_proxies = get_proxies(local_filename)
                    proxies.extend(new_proxies)
                    logging.info(f"Đã tải về {len(new_proxies)} proxy từ {link}")
                except requests.exceptions.RequestException as e:
                    logging.error(f"Không thể truy cập vào {link}: {str(e)}")
            else:
                logging.error(f"Không thể tải tệp từ {link} do không có tên tệp.")
    return proxies


def save_unused_proxies(filename, proxies):
    with open(filename, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")


def send_request(url, proxies, proxy):
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        logging.info(f"Request sent to {url} with proxy {proxy}")
        logging.info(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
        return True
    except Exception as e:
        logging.error(f"Failed to send request with proxy {proxy}. Reason: {e}")
        logging.info(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
        return False


def send_request_http(url, proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }
    return send_request(url, proxies, proxy)


def send_request_socks4(url, proxy):
    proxies = {
        "http": "socks4://" + proxy,
        "https": "socks4://" + proxy
    }
    return send_request(url, proxies, proxy)


def send_request_socks5(url, proxy):
    proxies = {
        "http": "socks5://" + proxy,
        "https": "socks5://" + proxy
    }
    return send_request(url, proxies, proxy)


def main():
    global used_proxies
    global successful_requests
    setup_logging()

    url = [input("Nhập vào link bạn muốn click: ") for _ in range(int(input("Nhập số lượng link: ")))]
    num_threads = int(input("Nhập số lượng luồng tối đa: "))
    delay = int(input("Nhập thời gian delay giữa các yêu cầu (giây): "))
    max_successful_requests = int(input("Nhập số lượng yêu cầu thành công tối đa: "))

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

    specific_countries = None
    if input("Bạn có muốn sử dụng proxy của các quốc gia cụ thể không? (y/n) ").lower() == "y":
        num_countries = int(input("Nhập số lượng quốc gia: "))
        specific_countries = [input(f"Nhập vào tên quốc gia {i+1}: ") for i in range(num_countries)]

    successful_requests = 0
    used_proxies = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for proxy_type, proxies in enumerate([proxies_http, proxies_socks4, proxies_socks5]):
            for proxy in proxies:
                proxy_parts = proxy.split(":")
                if len(proxy_parts) != 2:
                    logging.info(f"Proxy {proxy} không hợp lệ. Bỏ qua...")
                    continue

                ip, port = proxy_parts
                country_code, country = get_country_info(ip)
                if specific_countries is not None and country_code not in specific_countries:
                    logging.info(f"Proxy {proxy} không phải là của {'/'.join(specific_countries)}. Nó thuộc quốc gia {country}. Bỏ qua...")
                    continue

                if proxy_type == 0:  # http proxy
                    futures = [executor.submit(send_request_http, u, proxy) for u in url]
                elif proxy_type == 1:  # socks4 proxy
                    futures = [executor.submit(send_request_socks4, u, proxy) for u in url]
                else:  # socks5 proxy
                    futures = [executor.submit(send_request_socks5, u, proxy) for u in url]

                for future in futures:
                    if future.result():
                        successful_requests += 1
                        if successful_requests >= max_successful_requests:
                            logging.info(f"Đã đạt đến số lượng yêu cầu thành công tối đa ({max_successful_requests}). Dừng chương trình.")
                            return
                    else:
                        logging.info(f"Failed to send request with proxy {proxy}. Bỏ qua...")
                        continue
                used_proxies.append(proxy)
                if country_code and country:
                    logging.info(f"Proxy {proxy} thuộc quốc gia {country} ({country_code})")
                else:
                    logging.info(f"Proxy {proxy} không xác định quốc gia")
                logging.info(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
                sleep(delay)

        proxies_http = [p for p in proxies_http if p not in used_proxies]
        proxies_socks4 = [p for p in proxies_socks4 if p not in used_proxies]
        proxies_socks5 = [p for p in proxies_socks5 if p not in used_proxies]

        save_unused_proxies(filename_http, proxies_http)
        save_unused_proxies(filename_socks4, proxies_socks4)
        save_unused_proxies(filename_socks5, proxies_socks5)


if __name__ == "__main__":
    main()
