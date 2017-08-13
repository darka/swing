from __future__ import print_function
import sys
import pickle

import dateparser

def load_dump(filename):
    return pickle.load(open(filename))
    
def fix_date_hack(date):
    return date.replace('Septemer', 'September')

def print_classes(classes):
    location_classes = []
    for location, ls in classes.iteritems():
        if not ls:
            print('{}: NO DATA'.format(location), file=sys.stderr)
            continue
        for date, level, contents in ls:
            parsed_date = dateparser.parse(fix_date_hack(date), settings={'DATE_ORDER': 'DMY'})
            if not parsed_date:
                print(u'{}: failed to parse date: {}'.format(location, date), file=sys.stderr)
                continue
            location_classes.append((location, parsed_date.date(), level, contents))

    for location, date, level, contents in sorted(location_classes, key=lambda x: x[1]):
        print('{} {} ({}) {}'.format(*[s.encode('utf-8') for s in str(date), contents, level, location]))

def main():
    if len(sys.argv) != 2:
        print('Please specify dump filename', file=sys.stderr)
        sys.exit(1)

    classes = load_dump(sys.argv[1])
    print_classes(classes)

if __name__ == '__main__':
    main()
