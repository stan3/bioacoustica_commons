
from dwca.read import DwCAReader
from dwca.darwincore.utils import qualname as qn

def read_items(filename):
    with DwCAReader(filename) as dwca:
        for core_row in dwca:
            # core_row is an instance of dwca.rows.CoreRow
            if not core_row.extensions:
                continue
            core = dict(core_row.data.items())
            core['id'] = core_row.id
            # skip = False
            for extension_row in core_row.extensions:
                if extension_row.rowtype == 'http://rs.gbif.org/terms/1.0/Image':
                    # print(extension_row)
                    d = core.copy()
                    # d['extension'] = extension_row.rowtype
                    d.update(dict(extension_row.data.items()))
                    # items.append(d)
                    if d.get('http://purl.org/dc/terms/format') == 'audio/x-wav':
                        yield d


def xml_item(name, text):
  print("  <%s>%s</%s>" % (name, text, name))

if __name__ == '__main__':
    CC_BY = '//creativecommons.org/licenses/by/3.0/'
    ALLOWED_LICENSES = ['//creativecommons.org/licenses/by/3.0/']
    DISALLOWED_LICENSES = ['//creativecommons.org/licenses/by-nc-sa/3.0/']

    SCIENTIFIC_NAME = 'http://rs.tdwg.org/dwc/terms/scientificName'
    LICENSE = 'http://purl.org/dc/terms/license'

    USAGE_TERMS = 'http://ns.adobe.com/xap/1.0/rights/UsageTerms'
    URI = 'http://rs.tdwg.org/ac/terms/accessURI'
    FORMAT = 'http://purl.org/dc/terms/format'
    DOCUMENT = 'http://eol.org/schema/media/Document'
    WAV = 'audio/x-wav'
    TITLE = 'http://purl.org/dc/terms/title'

    print('<items>')
    for item in items[:10]:
        if item.get(USAGE_TERMS) == CC_BY and item.get(FORMAT) == WAV:
            print('<record>')
            xml_item('scientific_name', item[SCIENTIFIC_NAME])
            xml_item('uri', item[URI])
            xml_item('usage_terms', 'http:' + item[USAGE_TERMS])
            xml_item('id', item['id'])
            xml_item('title', item[TITLE].rsplit('.', 1)[0])
            print('</record>')
    print('</items>')
