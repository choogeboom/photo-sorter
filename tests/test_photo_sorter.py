import datetime
import pathlib

import py
import pytest
import photo_sorter as ps

test_file_dir = pathlib.Path('tests/files')


def _copy(self, target):
    import shutil
    assert self.is_file()
    shutil.copy(self, target)


# noinspection PyUnresolvedReferences
pathlib.Path.copy = _copy


@pytest.fixture(scope='function')
def image_tempdir(tmpdir: py.path.local):
    photos_dir: pathlib.Path = tmpdir.mkdir('photos')
    for image_path in test_file_dir.iterdir():
        new_image_path = photos_dir / image_path.name
        image_path.copy(new_image_path)
    return pathlib.Path(photos_dir)


# noinspection PyShadowingNames
@pytest.fixture(scope='function',
                params=['2016_01_01', '2016_04_01', '2017_01_01', '2017_01_11',
                        '2017_02_12'])
def test_image(image_tempdir: pathlib.Path, request):
    test_image_path = image_tempdir / f'test_image_{request.param}.jpeg'
    date = datetime.datetime.strptime(request.param, '%Y_%m_%d').date()
    return {'path': test_image_path,
            'date': date}


# noinspection PyShadowingNames
def test_get_image_date(test_image: dict):
    date = ps.get_image_date(test_image['path'])
    assert date == test_image['date']


# noinspection PyShadowingNames
def test_is_empty_dir(image_tempdir):
    assert not ps.is_empty_dir(image_tempdir)
    empty_dir = image_tempdir / 'empty'
    empty_dir.mkdir()
    assert ps.is_empty_dir(empty_dir)


# noinspection PyShadowingNames
def test_sort_image(image_tempdir: pathlib.Path, test_image: dict):
    ps.sort_file(test_image['path'], image_tempdir)
