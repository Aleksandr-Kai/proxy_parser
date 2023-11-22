import requests
from bs4 import BeautifulSoup
import lxml
import base64

baseURL = 'http://free-proxy.cz'

cookies = {
    '_ga': 'GA1.1.2140881241.1700628904',
    '_ga_FS4ESHM7K5': 'GS1.1.1700628904.1.1.1700629004.0.0.0',
    'fp': '9179249ba121017e8f3cae3d27d1679a',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': '_ga=GA1.1.2140881241.1700628904; _ga_FS4ESHM7K5=GS1.1.1700628904.1.1.1700629004.0.0.0; fp=9179249ba121017e8f3cae3d27d1679a',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36',
}

def find_next_page(document):
    try:
        return document.find('div', class_='paginator').find('a', text='Next »').get('href')
    except Exception as ex:
        return ''

def grab_proxies(document):
    table_trs = document.find('table', id='proxy_list').find('tbody').find_all('tr')

    ip_list = []
    
    for tr in table_trs:
        try:
            ip = tr.find('td').find('script').text
        except Exception as ex:
            print(ex)
            continue

        if ip:
            ip = base64.b64decode(ip.split('"')[1]).decode('utf-8')
            port = tr.find('span', class_='fport').text
            protocol = '{0: <7}'.format(tr.find('small').text)
            ip_list.append(f'{protocol} {ip}:{port}')
            
        else:
            continue
    
    return ip_list

def get_ip_list(s, url):
    print(f'URL >>> {url}')
    response = s.get(url, cookies=cookies, headers=headers, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')

        ip_list = grab_proxies(soup)
        next_page = find_next_page(soup)
        print(f'Next page: {next_page}')
        if next_page != '':
            ip_list += get_ip_list(s, f'{baseURL}{next_page}')
        return ip_list
    else:
        print(f'Проблемы с запросом. Статус: {response.status_code}')

    return []

def print_countries(s):
    response = s.get(f'{baseURL}/en/proxylist/country/all/all/ping/all', cookies=cookies, headers=headers, verify=False)

    soup = BeautifulSoup(response.text, 'lxml')
    countries = soup.find('select', id='frmsearchFilter-country').find_all('option')

    for c in countries:
        short_name = c.get('value')
        name = c.text.split('(')[0].strip()
        print(f'[{short_name}] -- {name}')

def get_proxies():
    s = requests.Session()
    print_countries(s)
    selected_country = input('Select country: ')
    url = f'{baseURL}/en/proxylist/country/{selected_country}/all/ping/all'

    ip_list = get_ip_list(s, url)

    if len(ip_list) > 0:
        with open('ip_list.txt', 'w') as file:
            file.writelines(f'{ip}\n' for ip in ip_list)
        print(f'Собрано проксей: {len(ip_list)}')
    else:
        print('Проксей не обнаружено')

    
def main():
    get_proxies()        

if __name__ == "__main__":
    main()