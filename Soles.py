import os
import requests
import tempfile
import logging
from time import sleep
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from datetime import datetime

ua = UserAgent()
global used_proxies
global successful_requests
global checked_proxies
global used_proxies
successful_requests = 0
checked_proxies = 0
used_proxies = 0


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("log/log.txt")])


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def get_country_info(ip):
    global checked_proxies
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        checked_proxies += 1
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
                    logging.info(f"Downloaded {len(new_proxies)} proxies from {link}")
                except requests.exceptions.RequestException as e:
                    logging.error(f"Unable to access {link}: {str(e)}")
            else:
                logging.error(f"Unable to download file from {link} as it does not have a file name.")
    return proxies

def save_unused_proxies(filename, proxies):
    with open(filename, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def send_request(url, proxies, proxy):
    try:
        user_agent = ua.random
        headers = {
            "User-Agent": user_agent
        }
        response = requests.get(url, proxies=proxies, headers=headers, timeout=5)
        logging.info(f"Request sent to {url} with proxy {proxy} using User-Agent: {user_agent}")
        logging.info(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
        return True
    except Exception as e:
        logging.error(f"Failed to send request with proxy {proxy}. Reason: {e}")
        logging.info(f"Used proxies: {len(usedproxies)}, Successful requests: {successful_requests}")
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
    log_folder = os.path.join(os.getcwd(), 'log')
    create_folder_if_not_exists(log_folder)

    log_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    current_log_folder = os.path.join(log_folder, log_datetime)
    create_folder_if_not_exists(current_log_folder)
    
    setup_logging(current_log_folder)

    url = [input("Enter the URL you want to click: ") for _ in range(int(input("Enter the number of URLs: ")))]
    num_threads = int(input("Enter the maximum number of threads: "))
    delay = int(input("Enter the delay between requests (in seconds): "))
    max_successful_requests = int(input("Enter the maximum number of successful requests: "))

    if input("Do you want to input a file containing links with proxies? (y/n) ").lower() == "y":
        filename_http_links = input("Enter the filename containing http proxy links: ")
        filename_socks4_links = input("Enter the filename containing socks4 proxy links: ")
        filename_socks5_links = input("Enter the filename containing socks5 proxy links: ")
        proxies_http = get_proxies_from_links_file(filename_http_links)
        proxies_socks4 = get_proxies_from_links_file(filename_socks4_links)
        proxies_socks5 = get_proxies_from_links_file(filename_socks5_links)
    else:
        filename_http = input("Enter the filename containing http proxies: ")
        filename_socks4 = input("Enter the filename containing socks4 proxies: ")
        filename_socks5 = input("Enter the filename containing socks5 proxies: ")
        proxies_http = get_proxies(filename_http)
        proxies_socks4 = get_proxies(filename_socks4)
        proxies_socks5 = get_proxies(filename_socks5)

    specific_countries = None
    if input("Do you want to use proxies from specific countries? (y/n) ").lower() == "y":
        num_countries = int(input("Enter the number of countries: "))
        specific_countries = [input(f"Enter the country name {i+1}: ") for i in range(num_countries)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for proxy_type, proxies in enumerate([proxies_http, proxies_socks4, proxies_socks5]):
            for proxy in proxies:
                proxy_parts = proxy.split(":")
                if len(proxy_parts) != 2:
                    logging.info(f"Invalid proxy {proxy}. Skipping...")
                    continue

                ip, port = proxy_parts
                country_code, country = get_country_info(ip)
                if specific_countries is not None and country_code not in specific_countries:
                    logging.info(f"Proxy {proxy} does not belong to {'/'.join(specific_countries)} countries. It belongs to {country}. Skipping...")
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
                        used_proxies += 1
                        if successful_requests >= max_successful_requests:
                            logging.info(f"Reached the maximum number of successful requests ({max_successful_requests}). Stopping the program.")
                            return
                    else:
                        logging.info(f"Failed to send request with proxy {proxy}. Skipping...")
                    logging.info(f"Checked proxies: {checked_proxies}, Used proxies: {used_proxies}, Successful requests: {successful_requests}")
                    continue
                used_proxies.append(proxy)
                if country_code and country:
                    logging.info(f"Proxy {proxy} belongs to {country} ({country_code})")
                else:
                    logging.info(f"Proxy {proxy} does not have a country identified")
                logging.info(f"Used proxies: {len(used_proxies)}, Successful requests: {successful_requests}")
                sleep(delay)

        proxies_http = [p for p in proxies_http if p not in used_proxies]
        proxies_socks4 = [p for p in proxies_socks4 if p not in used_proxies]
        proxies_socks5 = [p for p in proxies_socks5 if p not in used_proxies]

        save_unused_proxies(filename_http, proxies_http)
        save_unused_proxies(filename_socks4, proxies_socks4)
        save_unused_proxies(filename_socks5, proxies_socks5)

        # Save statistics to Statistics_log.txt
        statistics_log_path = os.path.join(current_log_folder, 'Statistics_log.txt')
        with open(statistics_log_path, 'w') as f:
            f.write(f"Total proxies downloaded: {len(proxies_http) + len(proxies_socks4) + len(proxies_socks5)}\n")
            f.write(f"Total proxies used: {used_proxies}\n")
            f.write(f"Total proxies checked for country: {checked_proxies}\n")
            f.write(f"Total proxies checked successfully: {checked_proxies - used_proxies}\n")
            if specific_countries:
                f.write(f"Total proxies matching input countries: {len(used_proxies)}\n")
            f.write(f"Total successful requests: {successful_requests}\n")
            f.write(f"Total failed requests: {max_successful_requests - successful_requests}\n")
            f.write("Fake User-Agent statistics:\n")
            ua_stats = ua.get_stats()
            for device, browsers in ua_stats.items():
                f.write(f"Device: {device}\n")
                for browser, count in browsers.items():
                    f.write(f"- {browser}: {count}\n")
            f.write(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Move log.txt, successful_requests.txt and Statistics_log.txt to the current log folder
        log_path = os.path.join(current_log_folder, 'log.txt')
        successful_requests_path = os.path.join(current_log_folder, 'successful_requests.txt')
        os.rename(os.path.join(log_folder, 'log.txt'), log_path)
        os.rename(os.path.join(log_folder, 'successful_requests.txt'), successful_requests_path)

if __name__ == "__main__":
    main()