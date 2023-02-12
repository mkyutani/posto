#!/usr/bin/env python3

import io
import os
import re
import requests
import sys

def send():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

    url = os.environ.get('TEAMS_WEBHOOK')

    import argparse
    parser = argparse.ArgumentParser(description='Send incoming webhook')
    parser.add_argument('-t', '--text', nargs=1, help=f'text to send')
    parser.add_argument('-u', '--url', nargs=1, help=f'webhook url (default: {url})')

    args = parser.parse_args()

    if args.text:
        text = args.text[0]
    else:
        text = sys.stdin.read()

    first_line_matched = re.match(r'^(#[^\n\r]*)(\n|\r)', text)
    if first_line_matched:
        title = first_line_matched.group(1)
        text = text[first_line_matched.end():]
    else:
        title = ''

    text = re.sub(r'[\n\r]', r'  \n', text)

    message = {
        'type': 'message',
        'attachments': [
            {
                'contentType': 'application/vnd.microsoft.teams.card.o365connector',
                'content': {
                    '@type': 'MessageCard',
                    '@context': 'https://schema.org/extensions',
                    'title': title,
                    'sections': [
                        {
                            'text': text
                        }
                    ]
                }
            }
        ]
    }

    if args.url:
        url = args.url[0]

    if not url:
        print('No webhook url ($TEAMS_WEBHOOK or -u parameter is necessary)', file=sys.stderr)
        exit(1)

    res = None
    try:
        res = requests.post(url, json=message)
    except Exception as e:
        print(e, file=sys.stderr)

    if res:
        status = res.status_code
    else:
        status = None

    print(f'{status}')

    if status is None or status >= 400:
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(send())