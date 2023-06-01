import json
import copy


def parse_cookie(_cookie: dict, _cookie_template: dict) -> dict:
    new_cookie = copy.deepcopy(_cookie_template)
    for item in _cookie.items():
        if item[0] == 'Name raw':
            new_cookie['name'] = _cookie['Name raw']
        elif item[0] == 'Content raw':
            new_cookie['value'] = _cookie['Content raw']
        elif item[0] == 'Path raw':
            new_cookie['path'] = _cookie['Path raw']
        elif item[0] == 'Host raw':
            i = 8
            if _cookie['Host raw'] == 'https://.google.com/'\
                    or _cookie['Host raw'] == 'https://.google.com.mx/':
                i += 1
            new_cookie['domain'] = _cookie['Host raw'][i:-1]
        elif item[0] == 'Expires raw':
            new_cookie['expires'] = int(_cookie['Expires raw'])
        elif item[0] == 'Send for raw':
            new_cookie['secure'] = bool(_cookie['Send for raw'].capitalize())
        elif item[0] == 'HTTP only raw':
            new_cookie['httpOnly'] = bool(_cookie['HTTP only raw'].capitalize())
        elif item[0] == 'SameSite raw':
            if _cookie['SameSite raw'] == 'no_restriction':
                new_cookie['sameSite'] = 'None'
            else:
                new_cookie['sameSite'] = _cookie['SameSite raw'].capitalize()
    return new_cookie


def parse_all():
    cookie_template = {
        'name': 'cookie_name',
        'value': 'cookie_value',
        'path': '/',
        'domain': 'example.com',
        'expires': 1677721600,  # Example expiry time for June 30, 2023
        'secure': True,
        'httpOnly': True,
        'sameSite': 'Strict'
    }
    with open('data/cookies.json', 'r') as cookies_file:
        cookies = json.load(cookies_file)
    new_cookies = [parse_cookie(cookie, cookie_template) for cookie in cookies]
    return new_cookies
