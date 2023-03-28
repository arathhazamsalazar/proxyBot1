import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv
from multiprocessing import Pool, Manager
from multiprocessing.pool import ThreadPool

def run_chrome(proxy, success_list):
    try:
        # Set the proxy for the current iteration
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=NetworkService")

        chrome = webdriver.Chrome(options=chrome_options)

        # Navigate to the website with the current instance of Chrome
        chrome.get("https://www.whatsmyip.org")

        # Check if the page loaded successfully
        if "404 Not Found" in chrome.page_source:
            raise Exception("Page not found error")

        # Click size
        size_button = chrome.find_elements(By.CSS_SELECTOR, '.size-grid-dropdown')
        for size_button in size_button:
            if size_button.text == 'CM 29.5':
                size_button.click()
                break
        time.sleep(2)

        # Click buy button
        size_button = chrome.find_elements(By.CSS_SELECTOR, '.buying-tools-cta-button')
        for size_button in size_button:
            if size_button.text == 'Comprar $4,399.00':
                size_button.click()
                break

        # Print a message and add the proxy to the success list
        print(f"Proxy {proxy} se ejecutó con éxito!!")
        success_list.append(proxy)

    except Exception as e:
        print(f"Error en proxy {proxy} ({time.strftime('%Y-%m-%d %H:%M:%S')}): {e}")

    finally:
        # Close the current window
        chrome.quit()

if __name__ == '__main__':
    # Read the proxy list from file
    with open('proxy_list.txt', 'r') as f:
        proxy_list = [line.strip() for line in f]

    with Manager() as manager:
        success_list = manager.list()

        # Check if the file exists
        if os.path.isfile('success_list.txt'):
            # Read the existing proxies from the file
            with open('success_list.txt', 'r') as f:
                existing_proxies = set([line.strip() for line in f])
        else:
            # Create an empty set if the file doesn't exist
            existing_proxies = set()

        # Run the function for each proxy in parallel, limited to 10 processes
        with ThreadPool(processes=10) as pool:
            pool.starmap(run_chrome, [(proxy, success_list) for proxy in proxy_list[:10]])

        # Remove the first 10 proxies from the proxy list file
        with open('proxy_list.txt', 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            f.writelines(lines[10:])

        # Write the successful proxies to a file
        with open('success_list.txt', 'a') as f:
            for proxy in success_list:
                print(proxy)

        # Overwrite the content of the success_list file
        with open('success_list.txt', 'w') as f:
            for proxy in existing_proxies | set(success_list):
                f.write(proxy + "\n")

