
import csv
import pprint
import sys

import biodwca


if __name__ == "__main__":
    dwca_items = {}
    for item in biodwca.read_items(sys.argv[1]):
        dwca_items[item['id']] = item

    with open(sys.argv[2]) as csvfile:
        writer = csv.writer(sys.stdout)
        for row in csv.reader(csvfile):
            # pprint.pprint(dwca_items[row[1]])
            interested = [
                'http://rs.tdwg.org/dwc/terms/scientificName',
                'http://rs.tdwg.org/dwc/terms/scientificNameAuthorship',
                'http://rs.tdwg.org/dwc/terms/taxonomicStatus',
            ]
            item = dwca_items[row[1]]
            writer.writerow([row[0]] + [item[key] for key in interested])
