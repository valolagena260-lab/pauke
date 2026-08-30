import base64
import urllib.request
import urllib.error
import re
import json
import sys

ENCODED_SOURCE = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2FidXNhZWVpZHgvSVBUVi1TY3JhcGVyLVppbGxhL3JlZnMvaGVhZHMvbWFpbi9CRC5tM3U='
ENCODED_TARGET = 'aHR0cHM6Ly9ibGRjbXByb2QtY2RuLnRvZmZlZWxpdmUuY29t'

def decode_string(encoded_bytes):
    """Decodes a base64 encoded string."""
    return base64.b64decode(encoded_bytes).decode('utf-8')

def fetch_playlist_content(url):
    """Fetches the playlist content from the given URL with a specific User-Agent."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return None

def parse_m3u(content, filter_string):
    channels = []
    lines = content.split('\n')
    
    current_channel = {
        "name": "",
        "logo": "",
        "link": "",
        "cookie": ""
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#EXTINF:'):
            logo_match = re.search(r'tvg-logo="(.*?)"', line)
            if logo_match:
                current_channel['logo'] = logo_match.group(1).strip()
            
            name_match = re.search(r',(?=[^"]*$)(.*)$', line)
            if name_match:
                raw_name = name_match.group(1).strip()
            else:
                last_comma = line.rfind(',')
                raw_name = line[last_comma + 1:].strip() if last_comma != -1 else "Unknown Channel"
            
            current_channel['name'] = raw_name.replace('[BD]', '').strip()

        elif line.startswith('#EXTHTTP:'):
            cookie_match = re.search(r'#EXTHTTP:{"cookie":"(.*?)"}', line)
            if cookie_match:
                current_channel['cookie'] = cookie_match.group(1).strip()

        elif not line.startswith('#'):
            current_channel['link'] = line
            
            if filter_string in line:
                channels.append(current_channel.copy())
            
            current_channel = {
                "name": "",
                "logo": "",
                "link": "",
                "cookie": ""
            }

    return channels

def main():
    source_url = decode_string(ENCODED_SOURCE)
    target_filter = decode_string(ENCODED_TARGET)

    content = fetch_playlist_content(source_url)

    if content:
        extracted_channels = parse_m3u(content, target_filter)
        
        json_output = json.dumps(extracted_channels, indent=4, ensure_ascii=False)
        
        print("Content-Type: application/json\n")
        print(json_output)
        
        with open('hummer.json', 'w', encoding='utf-8') as f:
            f.write(json_output)
    else:
        print("Content-Type: application/json\n")
        print(json.dumps({"error": "Failed to fetch playlist"}))

if __name__ == "__main__":
    main()
