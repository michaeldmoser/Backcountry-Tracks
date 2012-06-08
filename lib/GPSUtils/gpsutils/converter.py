import subprocess

class GPSFormatConverter(object):
    def __init__(self, gps_document):
        self.input_document = gps_document.strip()
        self.format = 'unknown'

        if (self.input_document.startswith('<?xml')):
            if self.input_document.endswith('</kml>'):
                self.format = 'kml'
            elif self.input_document.endswith('</gpx>'):
                self.format = 'gpx'

        if self.format == 'unknown':
            raise RuntimeError('The file is not supported or is not a valid map file. Please use a GPX or KML file.')

    def convert(self, to_format):
        '''Converts a GPSDocument to to_format'''
        if to_format == self.format:
            return self.input_document
        gpsbabel = subprocess.Popen(
                ['gpsbabel', '-i', self.format, '-f', '-', '-o', to_format, '-F', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
                )

        output, error = gpsbabel.communicate(self.input_document)

        return output
