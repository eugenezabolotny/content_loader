import os
import shutil
import json
import re

PATH_FROM = '/home/eugene/Videos/mediadata/'
PATH_TO = '/home/eugene/Videos/storage/'

extra_metadata = os.path.join(PATH_FROM, 'metadata.json')
storage_metadata = os.path.join(PATH_TO, 'config/metadata.json')
storage_movies = os.path.join(PATH_TO, 'movies/')


def is_metadata_exists():
    """
    Checks if external and internal metadata.json files exists

    :return: bool, True if both exists
    """
    return os.path.exists(storage_metadata) and os.path.exists(extra_metadata)


def update_movie_object(ext_movie, int_metadata):
    """
    Updates movie object according to internal metadata.json file.

    :param ext_movie: dict, movie object from external storage metadata.json file
    :param int_metadata: dict, internal metadata.json file
    :return: dict, updated movie object
    """
    ext_movie['id'] = int_metadata['movies'][-1]['id'] + 1

    movie_filename = ext_movie['path']
    if len(ext_movie['path'].split('/')) > 1:
        movie_filename = ext_movie['path'].split('/')[-1]

    movie_dirname = ext_movie['name'].lower()
    regex = re.compile('[^a-z0-9 ]')
    movie_dirname = regex.sub('', movie_dirname)
    movie_dirname = ' '.join(movie_dirname.split())
    movie_dirname = movie_dirname.replace(' ', '-')

    ext_movie['path'] = 'api/src/movies/mv-' + movie_dirname + '/' + movie_filename

    ext_movie['cover'] = ext_movie['cover'].split('/')[-1]

    return ext_movie


def copy_movie(ext_movie, int_movie):
    """
    Copies movie file with all files related to it from external to internal storage.

    :param ext_movie: dict, movie object from external storage metadata.json file
    :param int_movie: dict, movie object from internal storage metadata.json file
    :return: Null
    """
    cover_src = os.path.join(PATH_FROM, ext_movie['cover'])
    cover_dst = storage_movies
    shutil.copy(cover_src, cover_dst)

    movie_src = os.path.join(PATH_FROM, ext_movie['path'])
    movie_dst = os.path.join(storage_movies, int_movie['path'].split('/')[-2] + '/')
    if not os.path.exists(movie_dst):
        os.mkdir(movie_dst)
    if movie_src.split('.')[-1] == 'm3u8':
        shutil.copy(movie_src, movie_dst)
        with open(movie_src) as file:
            for row in file:
                if row[0] != '#':
                    movie_src = movie_src.rsplit('/', 1)[0] + '/' + row.strip()
                    shutil.copy(movie_src, movie_dst)
    else:
        shutil.copy(movie_src, movie_dst)


def extend_media():
    """
    Extends media in internal storage by media from external storage.

    :return: Null
    """
    if is_metadata_exists():
        with open(storage_metadata, encoding="utf-8") as json_file:
            json_metadata = json.load(json_file)
        with open(extra_metadata, encoding="utf-8") as json_file:
            json_extra_metadata = json.load(json_file)

        for movie in json_extra_metadata['movies']:
            original_movie = movie.copy()
            if not any(next_movie['name'] == movie['name'] for next_movie in json_metadata['movies']):
                new_movie = update_movie_object(movie, json_metadata)
                json_metadata['movies'].append(new_movie)
                copy_movie(original_movie, new_movie)

        with open(storage_metadata, 'w') as outfile:
            json.dump(json_metadata, outfile, indent=4, sort_keys=True)
    else:
        pass


if __name__ == '__main__':
    extend_media()
    print('extend_media: done')
