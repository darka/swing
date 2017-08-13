import pickle
import re
import requests
from bs4 import BeautifulSoup

ALL_CLASS_URL = 'http://www.swingpatrol.co.uk/class-timetable/'

CLASS_DUMP_FILENAME = 'classes.dump'

def load_url(url):
    response = requests.get(url)
    html = response.content
    return BeautifulSoup(html, 'html5lib')

def retrieve_locations():
    soup = load_url(ALL_CLASS_URL)
    tables = soup.findAll('table', attrs={'class': 'class-table'})
    ret = {}
    for table in tables:
        for row in table.findAll('tr'):
            if not row.text:
                continue
            link = row.find('a')
            ret[link.text] = link['href']
    return ret

def find_class_plan(url):
    soup = load_url(url)
    class_plan_anchor = soup.find('a', attrs={'href': re.compile('.*class-plan.*')})
    if not class_plan_anchor:
        return None
    return class_plan_anchor['href']

def class_list(url):
    print('retrieving: {}'.format(url))
    soup = load_url(url)

    ret = []

    tables = soup.find_all('table', attrs={'class': 'ox_table'})
    for table in tables:
        header_cells = table.find('thead').findAll('th')
        levels = [
            cell.text
            for cell in header_cells
            if re.match('.*Level.*', cell.text, re.I)
        ]
        body = table.find('tbody')
        if not body:
            break
        body_rows = body.findAll('tr')
        for row in body_rows:
            if not row:
                continue
            row = row.findAll('td')

            date = row[0]
            if re.match('.*Teacher.*', header_cells[1].text):
                class_column_start_index = 2
            else:
                class_column_start_index = 1

            for i, class_contents in enumerate(row[class_column_start_index:]):
                ret.append([text.strip() for text in (date.text, levels[i], class_contents.text)])
    return ret

def dump_classes():
    locations = retrieve_locations()
    extracted_data = {}
    for location, url in locations.iteritems():
        url = find_class_plan(url)
        if url:
            classes = class_list(url)
            extracted_data[location] = classes
        else:
            extracted_data[location] = None
    print('dumping to: {}'.format(CLASS_DUMP_FILENAME))
    pickle.dump(extracted_data, open(CLASS_DUMP_FILENAME, 'w'))

def main():
    dump_classes()

if __name__ == '__main__':
    main()
