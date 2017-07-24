#!/usr/bin/env python3

import sys
import pywikibot

def read_categories(filename):
    with open(filename) as f:
        for line in f:
            split = line.strip().split(',', 3)
            if split[0].startwith('#'):
                continue
            if len(split) > 1:
                checked = len(split) == 3 and split[2] == 'checked'
                yield(split[0], split[1], checked)


if __name__ == '__main__':
    site = pywikibot.Site(fam='commons', user='BioUploadBot')
    site.login()
    missing_categories = {}
    for existing, new, checked in read_categories(sys.argv[1]):
        if checked:
            page = pywikibot.Category(site, 'Category:' + new)
            if page.exists():
                continue
            text = ['[[Category:%s]]' % new.replace(' ', '|')]
            # text.append('{{wikispecies|%s}}' % new.split()[0])
            page.text = '\n'.join(text)
            page.save()
