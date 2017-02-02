#!/usr/bin/env python3

import argparse
import itertools
import logging
import os
import pprint
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

import pywikibot
import xlrd

import biodwca


def upload_wav_as_flac(url, site, imagepage):
    if not url.endswith('.wav'):
        raise RuntimeError('need .wav extension')
    tempdir = tempfile.mkdtemp(prefix='bot-')
    try:
        # local_filename, headers = urllib.request.urlretrieve(url, os.path.join(tempdir, 'in.wav'))
        wav_filename = os.path.join(tempdir, 'in.wav')
        flac_filename = os.path.join(tempdir, 'out.flac')
        subprocess.check_call(['curl', '--retry', '3', '-o', wav_filename, url])
        subprocess.check_call(['flac', '--best', '-o', flac_filename, wav_filename])
        site.upload(imagepage, source_filename=flac_filename, comment='Initial upload of file')
        logging.info('creating page http:%s', imagepage.permalink())
    finally:
        shutil.rmtree(tempdir, True)


def upload_or_update(site, url, filename, text):
    imagepage = pywikibot.FilePage(site, filename)  # normalizes filename
    if imagepage.exists():
        if imagepage.text != text:
            # print(repr(imagepage.text))
            # print(repr(text))
            logging.info('updating page http:%s', imagepage.permalink())
            # print(imagepage.permalink())
            #print(imagepage.latest_file_info)
            imagepage.text = text
            imagepage.save()
        else:
            logging.debug('page unchanged http:%s', imagepage.permalink())
    else:
        imagepage.text = text
        # https://phabricator.wikimedia.org/diffusion/PWBC/browse/master/scripts/upload.py
        # site.upload(imagepage, source_url=url)
        upload_wav_as_flac(url, site, imagepage)
    # pywikibot.output(u'Uploading file to %s via API...' % site)


def read_xls_by_species_id(filename):
    d = {}
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)

    header = [c.value for c in sheet.row(0)]
    cols = dict(zip(header, range(sheet.ncols)))
    for row_index in range(1, sheet.nrows):
        key = (sheet.cell(row_index, cols['Recording (Filename)']).value,
               sheet.cell(row_index, cols['Species (GUID)']).value)
        if '' in key:
            continue
        if key in d:
            logging.error('read_xls_by_species_id: %s already set', key)
        d[key] = \
            dict(zip(header, (sheet.cell(row_index, col_index).value for col_index in range(sheet.ncols))))
        # values.append(sheet.cell(row_index, col).value)
        # d[sheet.cell(row_index, cols['Species (GUID)']).value] = sheet.row(row_index)
    return d


def make_id(s):
    return re.sub('[. ():%&-]', '', re.sub('/+', '_', s))


def check_category(site, item):
    # if item['http://rs.tdwg.org/dwc/terms/taxonRank'] == 'Subspecies':
    #     category = item['http://rs.tdwg.org/dwc/terms/scientificName'].rsplit(maxsplit=1)[0]
    #     logging.verbose('Subspecies', item['http://rs.tdwg.org/dwc/terms/scientificName'])
    # else:
    category = item['http://rs.tdwg.org/dwc/terms/scientificName']

    if category == 'Mesambria dubia':
        # a synonmn
        category = 'Cingalia dubia'
    if category == 'Chorthippus Glyptobothrus yersini':
        # Glyptobothrus otherwise in brackets, seems subgenus
        category = 'Chorthippus yersini'

    # shorthand for an unspecified species of x
    if category.endswith(' sp.'):
        category = category[:-len(' sp.')]

    if not pywikibot.Category(site, 'Category:' + category).exists():
        raise RuntimeError("Category doesn't exist: \"%s\"" % category)
    item['wikipedia_category'] = category


def check_license(item):
    licenses = {'//creativecommons.org/licenses/by/3.0/': 'Cc-by-3.0'}
    license = item['http://purl.org/dc/terms/license']
    if license in licenses:
        item['wikimedia_permission_template'] = licenses[license]
    else:
        raise RuntimeError('Unsupported license: %s' % license)


def add_unit(item, keys, suffix):
    for key in keys:
        if item[key]:
            item[key] = '%s %s' % (item[key], suffix)


def get_access_uri(item):
    return item['http://purl.org/dc/terms/identifier']


def upload(site, item):
    filename = "BioAcoustica_%s.flac" % (item['http://purl.org/dc/terms/title'].rsplit('.', 1)[0])
    item['wikimedia_uri'] = get_access_uri(item)
    item = dict((make_id(key), value) for key, value in item.items())
    try:
        add_unit(item, ['TapeSpeedcm_s'], 'cm/s')
        add_unit(item, ['TemperatureInitialCelsius', 'TemperatureFInalCelsius'], 'c')
        add_unit(item, ['RelativeHumidityInitial', 'RelativeHumidityFinal'], '%')
        add_unit(item, ['MicrophonePowerSupplyDistancefromSubjectcm'], 'cm')
# New template created for this
# Alternate could be {{Musical work}} e.g.
# https://commons.wikimedia.org/wiki/File:Canada_Geese_(Branta_canadensis)_(W1CDR0001421_BD11).ogg

        upload_or_update(site, item['wikimedia_uri'], filename, """\
{{BioAcousticaSample
 |description        = Sound recording of %(http_rstdwgorg_dwc_terms_scientificName)s
 |date               = %(DateRecordedStart)s
 |source             = %(wikimedia_uri)s
 |permission         = {{%(wikimedia_permission_template)s}}
 |copyright holder   = %(CopyrightHolder)s
 |recorder           = %(Recorder)s
 |recorder power supply = %(PowerSupply)s
 |peak meter reading = %(PeakMeterReading)s
 |gain control position = %(GainControlPosition)s
 |tape = %(Tape)s
 |tape speed = %(TapeSpeedcm_s)s
 |track = %(Tracks)s
 |record local time = %(Localtime)s
 |reference signal = %(ReferenceSignal)s
 |temperature initial = %(TemperatureInitialCelsius)s
 |temperature final = %(TemperatureFInalCelsius)s
 |relative humidity initial = %(RelativeHumidityInitial)s
 |relative humidity final = %(RelativeHumidityFinal)s
 |light = %(Light)s
 |extraneous noise = %(ExtraneousNoise)s
 |substrate = %(Substrate_Cage)s
 |air movement = %(AirMovement)s
 |biotic factors = %(BioticFactors_ExperimentalConditions)s
 |microphone = %(MicrophonePowerSupplyMicrophonePowerSupply)s
 |microphone distance from subject = %(MicrophonePowerSupplyDistancefromSubjectcm)s
 |microphone windshield = %(MicrophonePowerSupplyWindshield)s
 |microphone reflector = %(MicrophonePowerSupplyReflector)s
 |microphone preamplifier = %(MicrophonePowerSupplyPreamplifier)s
 |microphone filter = %(MicrophonePowerSupplyFilter)s
}}

[[Category:%(wikipedia_category)s]]
[[Category:Files from BioAcoustica]]""" % item)
    except KeyError:
        pprint.pprint(item)
        raise


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    # httplib2 comes with it's on ca_certs that doesn't work with beta's letencrypt cert
    # this hack makes it use the default system one
    for thread in pywikibot.comms.http.threads:
        thread.http.ca_certs = False

    parser = argparse.ArgumentParser()
    parser.add_argument('dwca_zip')
    parser.add_argument('species_xls')
    parser.add_argument('--upload', action='store_true')
    args = parser.parse_args()

    site = pywikibot.Site('commons', 'commons')
    site_beta = pywikibot.Site('beta', 'commons')
    site_beta.login()
    items = biodwca.read_items(args.dwca_zip)
    # item = next(items)
    xls = read_xls_by_species_id(args.species_xls)

    skip = '''
http://bio.acousti.ca/sites/bio.acousti.ca/files/576_15_Locusta_migratoria_migratorioides_253b.wav
http://bio.acousti.ca/sites/bio.acousti.ca/files/437_6_Chorthippus_yersini_723r1.wav
http://bio.acousti.ca/sites/bio.acousti.ca/files/566_9_Ancistrura_nigrovittata_638r7.wav
http://bio.acousti.ca/sites/bio.acousti.ca/files/582_4_Chorthippus_yersini_805r2_14-Dec.wav
'''
    skip = skip.strip().split('\n')
    # print(skip)
    seen = []
    started_id = False
    for item in items:
        # pprint.pprint(item)
        uri = get_access_uri(item)
        logging.debug('processing %s - %s', item['id'], uri)
        if uri in seen:
            pprint.pprint(item)
            raise RuntimeError('already seen:' + uri)
        seen.append(uri)
        if uri in skip:
            logging.info('Skipping from skip list %s %s', item['id'], uri)
            continue
        try:
            # pprint.pprint(item)
            check_license(item)
            # print(item['http://purl.org/dc/terms/identifier'],
            #       item['http://rs.tdwg.org/ac/terms/accessURI'])
            check_category(site, item)
            xls_key = (item['http://purl.org/dc/terms/title'], item['id'])
            if xls_key in xls:
                item.update(xls[xls_key])
            else:
                logging.error('no xls item %s', xls_key)
                continue
            if type(item['Local time']) == float:
                item['Local time'] = int(item['Local time'])
            if args.upload:
                upload(site_beta, item)
        except RuntimeError as e:
            logging.error('%s, %s, %s' % (e, item['id'], get_access_uri(item)))
            # print(e, '-', item['id'], get_access_uri(item))
        except:
            pprint.pprint(item)
            raise
