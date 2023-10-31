import os
import requests
import time
import argparse
import threading
import queue
import itertools

FILETYPES = ['pptx', 'docx', 'txt']
LANGUAGES = ['en', 'fi', 'sv']

message_queue = queue.Queue()


def send_request(filepath, source, target, base_api_url):
    """
    Send a POST request with the file and the given source and target languages.
    """
    endpoint_url = f"{base_api_url}/translate_file"

    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        data = {'source': source, 'target': target}
        
        start_time = time.time()

        message_queue.put(f"Sent request to {endpoint_url} at {start_time}. File: {filepath}, Target: {target}.")
        response = requests.post(endpoint_url, files=files, data=data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            response_json = response.json()
            download_url = f"{base_api_url}/{response_json['translatedFileUrl']}"
            download_filename = os.path.join("translated_files", f"{target}_{os.path.basename(filepath)}")
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(download_filename, 'wb') as f_out:
                    for chunk in r.iter_content(chunk_size=8192):
                        f_out.write(chunk)

        # Add response message and statistics to the queue
        message_queue.put(f"File: {filepath}, Target: {target}, Duration: {duration:.2f} seconds, Response Status: {response.status_code}")


def print_messages():
    """
    Continuously print messages from the message_queue.
    """
    while True:
        message = message_queue.get()  # This will block until a message is available
        print(message)

def main(args):
    # Ensure the translated_files directory exists
    if not os.path.exists("translated_files"):
        os.makedirs("translated_files")

    # Start a thread dedicated to printing messages
    threading.Thread(target=print_messages, daemon=True).start()

    # Test dirs
    test_dirs = [f'{x[0]}_{x[1]}' for x in list(itertools.product(FILETYPES,LANGUAGES))]
    
    
    # Iterate over the subdirectories in the current directory
    for subdir, _, files in os.walk("."):
        # 
        if os.path.basename(subdir) not in test_dirs:
            continue
        
        source = os.path.basename(subdir).split("_")[-1]

        # Validate the extracted source
        if source not in LANGUAGES:
            message_queue.put(f"Invalid source in subdirectory name: {subdir}")
            continue
        
        targets = [lang for lang in LANGUAGES if lang != source]

        message_queue.put(f"Processing subdirectory: {subdir}")
        
        # Iterate over the files in the subdirectory
        for file in files:
            filepath = os.path.join(subdir, file)
            for target in targets:
                # Start a new thread for each request
                threading.Thread(target=send_request, args=(filepath, source, target, args.api_url)).start()
                time.sleep(args.delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send test requests to an API.")
    parser.add_argument("--api-url", required=True, help="Base API URL.")
    parser.add_argument("--delay", type=int, default=0, help="Delay between requests in seconds.")
    
    args = parser.parse_args()
    main(args)
