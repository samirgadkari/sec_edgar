'''
Get data from the given URL.
Extract tables from the HTML.
Convert HTML table to image.
Segment table image into cells.
Optical Character Recognition (OCR) of each cell.
Return JSON for each table in the file.
'''
from bs4 import BeautifulSoup
import imgkit
from PIL import Image
import random as rnd
import requests
import sys
import time

spreadsheet_doc_format = 'xml'
html_doc_format = 'html'
location = {}

def get_file(url, out_filename, timeout_range=None):
    '''Get file at the given url'''
    try:
        r = requests.get(url)

        if r.status_code != 200:
            print('Error: Status code:', r.status_code)
            return

        if (spreadsheet_doc_format not in r.headers['content-type']) and \
           (html_doc_format not in r.headers['content-type']):

            print('Error: content_type:', r.headers['content-type'])
            return

        with open(location['input'] + '/' + out_filename, 'wb') as f:
            f.write(r.content)

        if timeout_range != None:
            timeout = rnd.randint(timeout_range[0],
                                  timeout_range[1])
            print('Timing out for:', timeout, 'seconds')
            time.sleep(timeout)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def segment(filename):
    '''Segments an image into cells of a table'''
    im = Image.open(filename)
    pixels = im.load()

    # Since we're dealing with greyscale images only,
    # take the average of the RGB values as our pixel value.
    num_rows, num_cols = im.size
    greyscale = [[(pixels[i, j][0] + pixels[i, j][1] + pixels[i, j][2])/ 3 \
                  for j in range(num_cols)] for i in range(num_rows)]

    print('num_rows:', num_rows, 'num_cols:', num_cols)
    print('len(greyscale):', len(greyscale))
    print('len(greyscale[0]):', len(greyscale[0]))

    # Change image at transition points

    vertical_transitions = []
    for i in range(num_rows):
        for j in range(num_cols - 1):
            if greyscale[i][j] != greyscale[i][j+1]:
                vertical_transitions.append((i, j,
                                             greyscale[i][j],
                                             greyscale[i][j+1]))

    horizontal_transitions = []
    for j in range(num_cols):
        for i in range(num_rows - 1):
            if greyscale[i][j] != greyscale[i+1][j]:
                horizontal_transitions.append((i, j,
                                               greyscale[i][j],
                                               greyscale[i+1][j]))

    print(horizontal_transitions[:10])
    print(vertical_transitions[:10])

    # Remove all horizontal/vertical lines

    # Remove all colors other than black or white


    for (i, j, v1, v2) in horizontal_transitions:
        pixels[i, j] = (0, 255, 0, 255)

    for (i, j, v1, v2) in vertical_transitions:
        pixels[i, j] = (255, 0, 0, 255)

    im.save('with_color.png')

def process_file(filename):
    '''
    Extracts tables from HTML file.
    Outputs each table as an image file.
    Segments each image file into table cells.
    Performs OCR on each cell.
    Returns JSON for all tables in each HTML input file.
    '''
    try:
        with open(location['input'] + '/' + filename, 'r') as f:
            file_contents = f.read()

            soup = BeautifulSoup(file_contents, 'html.parser')
            tables = soup.select('table')

            filename_parts = filename.split('.')
            # for i in range(len(tables)):
            for i in range(5):
                if i != 4:
                    continue

                table = tables[i]
                image_filename = location['output'] + '/' + \
                                       filename_parts[0] + '_' + str(i) + '.png'
                imgkit.from_string(table.prettify(), image_filename)
                segment(image_filename)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def set_location(dir_type, d):
    global location
    location[dir_type] = d


set_location('input',  'data')
set_location('output', 'data/processed')
get_file('https://www.sec.gov/Archives/edgar/data'
         '/72971/000095014906000083/f17867exv13.htm', 'test.html')
process_file('test.html')
# get_file('https://sec.gov/Archives/edgar/data'
#            '/72971/000007297119000227/Financial_Report.xlsx',
#            timeout_range=[15, 30])

