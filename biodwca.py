
from dwca.read import DwCAReader
from dwca.darwincore.utils import qualname as qn

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
                d = core.copy()
                d['extension'] = extension_row.rowtype
                d.update(dict(extension_row.data.items()))
                # items.append(d)
                if d.get(USAGE_TERMS) == CC_BY and d.get(FORMAT) == WAV:
                    yield d


def xml_item(name, text):
  print("  <%s>%s</%s>" % (name, text, name))


if __name__ == '__main__':
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

        #
        #
        #
        #     if extension_row.rowtype == 'http://rs.gbif.org/terms/1.0/Image':
        #         license = extension_row.data['http://purl.org/dc/terms/license']
        #         if license in ALLOWED_LICENSES:
        #             pass
        #         elif license in DISALLOWED_LICENSES:
        #             skip = True
        #         else:
        #             raise RuntimeError('unknown license ' + license)
        # if skip:
        #     continue
        #
        # # print(type(core_row.data))
        # for key, value in core_row.data.items():
        #     if value:
        #         print(key, value)
        #
        # print('extenions')
        # for extension_row in core_row.extensions:
        #     print(extension_row.rowtype)
        # #     if extension_row.rowtype == 'http://rs.gbif.org/terms/1.0/Image':
        #         # if extension_row.data['http://purl.org/dc/terms/license'] == '//creativecommons.org/licenses/by/3.0/':
        #
        #     for key, value in extension_row.data.items():
        #         if value:
        #             print('  ', key, value)
        #             # print(core_row.data['http://rs.tdwg.org/dwc/terms/scientificName'], '-',
        #             #     extension_row.data['http://purl.org/dc/terms/identifier'])
        # print('')
        #
        # items.append(d)
        #     # print(row)
        # #print(type(core_row))
        # #print(dir(core_row))
        # # break
