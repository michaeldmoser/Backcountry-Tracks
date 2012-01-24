import unittest

import os.path

from gpsutils.converter import GPSFormatConverter

dir_path = os.path.dirname(__file__)

kml_path = os.path.join(dir_path, 'kml_document.kml')
KML_DOCUMENT = open(kml_path, 'r').read()
KML_DEFAULT_DOCUMENT = open(os.path.join(dir_path, 'kml_default_doc.kml'), 'r').read().strip()


gpx_path = os.path.join(dir_path, 'gpx_document.gpx')
GPX_DOCUMENT = open(gpx_path, 'r').read()
GPX_DEFAULT_DOCUMENT = open(os.path.join(dir_path, 'gpx_default_doc.gpx'), 'r').read().strip()

KML_DOC_START = '''<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns='''
GPX_DOC_START = '''<?xml version="1.0" encoding="UTF-8"?>\n<gpx'''

class TestConverter(unittest.TestCase):
    def test_converts_from_gpx_to_kml(self):
        '''Converts a GPX xml data to KML xml data'''
        converter = GPSFormatConverter(GPX_DOCUMENT)
        kml_doc = converter.convert('kml')

        passed = kml_doc.startswith(KML_DOC_START) and \
                kml_doc.strip() != KML_DEFAULT_DOCUMENT
        self.assertTrue(passed)

    def test_converts_from_kml_to_gps(self):
        '''Converts KML xml data to GPX xml data'''
        converter = GPSFormatConverter(KML_DOCUMENT)
        gpx_doc = converter.convert('gpx')
        passed = gpx_doc.startswith(GPX_DOC_START) and \
                gpx_doc.count('trkpt')
        self.assertTrue(passed)

    def test_converts_from_kml_to_kml(self):
        converter = GPSFormatConverter(KML_DOCUMENT)
        kml_doc = converter.convert('kml')

        passed = kml_doc.startswith(KML_DOC_START) and \
                kml_doc.strip() != KML_DEFAULT_DOCUMENT
        self.assertTrue(passed)


if __name__ == '__main__':
    unittest.main()

