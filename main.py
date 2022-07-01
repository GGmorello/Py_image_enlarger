import csv
import sys
import os
import urllib.request, urllib.error
import logging
from PIL import Image

logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO) # Metti DEBUG al posto di INFO se vuoi avere tutte le informazioni



def download(raw_link: str, count: int):
    try:
        payload = urllib.request.urlopen(raw_link)
        if payload.code == 200:
            with open('./tmp', 'wb') as handler:
                handler.write(payload.read())
            return True
        else:
            logging.error("Invalid link (line " + str(count+2) + "): " + raw_link)
            raise Exception
    except urllib.error.HTTPError as he:
        if he.code == 404:
            logging.error('Not Found (line ' + str(count+2) + '): ' + raw_link)
            return False
    except Exception as e:
        logging.error(str(e))
        if os.path.exists('./tmp'):
            os.remove('./tmp')
        sys.exit()


def process(row):
    try:
        with Image.open('tmp') as old_im:
            logging.debug(row)
            link, dirname, fname, b, l, r = row
            b, l, r = int(b), int(l), int(r)
            x, y = old_im.size
            t = (x + l + r - y - b)
            new_size = ((x + l + r), (t + y + b))
            if old_im.mode == 'P':
                old_im.convert('RGBA')
                new_im = Image.new("RGBA", new_size, (255, 255, 255))
                new_im.paste(old_im, (l, t, l+x, t+y), old_im)
            elif old_im.mode == 'RGB':
                new_im = Image.new("RGB", new_size, (255, 255, 255))
                new_im.paste(old_im, (l, t, l+x, t+y))
            elif old_im.mode == 'RGBA':
                new_im = Image.new("RGBA", new_size, (255, 255, 255))
                new_im.paste(old_im, (l, t, l+x, t+y), old_im)
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            new_im.save('./{}/{}'.format(dirname, fname), )
    except Exception as e:
        logging.error(str(e))
        if os.path.exists('./tmp'):
            os.remove('./tmp')
        sys.exit()


def main(file_in):
    logging.info("New process from file: " + file_in)
    with open(file_in, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for count, row in enumerate(csv_reader):
            link = row[0]
            if download(link, count):
                process(row)
        os.remove('./tmp')
        logging.info("Done\n")


if __name__ == '__main__':
    main('images.csv')
