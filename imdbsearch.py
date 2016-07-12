#!/usr/bin/env python
# encoding: utf-8

# Pierre-Olivier Vauboin <povauboin@gmail.com>

import os
import re
import sys
import glob
import string
import requests

def clean_name(film):
    basename = os.path.basename(film)
    name = '.'.join(basename.split('.')[:-1]) if '.' in basename else basename

    year = ''
    m = re.search('.+((19|20)[0-9]{2})', name)
    if m and len(m.groups()) > 1:
        year = m.group(1)
        name = name.split(year)[0]

    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = name.translate(string.maketrans('.-_()[]', ' '*7))

    keywords = keywords = ['Disc', 'CD', '720p', '1080p', 'x264']
    for keyword in keywords:
        name = name.split(keyword)[0]

    # print ('%s __ %s' % (name, year))
    return name.strip(' '), year

def find_imdb(film):
    r = requests.get('http://www.imdb.com/find?q=%s' % film)

    m = re.search('<a href="/title/(tt[0-9]+)/\?ref_=fn_al_tt_1" >', r.text)
    if not m or not len(m.groups()) == 1:
        print ('Search returned no results')
        return 0
    return score_imdb(m.group(1))

def score_imdb(index):
    r = requests.get('http://www.imdb.com/title/%s' % index)

    m = re.search('<span itemprop="ratingValue">([0-9]\.[0-9])</span>', r.text)
    if not m or not len(m.groups()) == 1:
        print ('Could not parse score')
        return 0
    return float(m.group(1))

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print ('usage: %s <film_dir>')
        sys.exit(1)

    film_dir = sys.argv[1]
    films_clean = set()
    for film in glob.glob(film_dir + '/*'):
        films_clean.add(clean_name(film))
    # print(films_clean)

    films_score = []
    for film, year in films_clean:
        sys.stdout.write('Searching %s [%s]... ' % (film, year))
        # score = find_imdb(' '.join([film, year]))
        score = find_imdb(film)
        sys.stdout.write('%s\n' % score)
        films_score.append([film, score])
    films_score.sort(key=lambda x: x[1], reverse=True)

    print ('')
    for film in films_score:
        print (film)
