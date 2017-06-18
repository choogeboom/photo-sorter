import datetime
import pathlib as pl

import py
import pytest
import photo_sorter as ps

test_file_dir = pl.Path('tests/files')


@pytest.fixture(scope='function', name='image_tempdir')
def make_image_tempdir(tmpdir: py.path.local) -> pl.Path:
    return pl.Path(tmpdir.mkdir('photos'))


@pytest.fixture(scope='function', name='unsorted_tempdir')
def make_unsorted_tempdir(image_tempdir: pl.Path) -> pl.Path:
    unsorted_dir = image_tempdir / 'unsorted'
    unsorted_dir.mkdir()
    for image_path in test_file_dir.iterdir():
        new_image_path = unsorted_dir / image_path.name
        image_path.copy(new_image_path)
    return unsorted_dir


@pytest.fixture(scope='function',
                params=[('2014_04_21', datetime.date(2014, 4, 21)),
                        ('2016_01_01', datetime.date(2016, 1, 1)),
                        ('2016_04_01', datetime.date(2016, 4, 1)),
                        ('2017_01_01', datetime.date(2017, 1, 1)),
                        ('2017_01_11', datetime.date(2017, 1, 11)),
                        ('2017_02_12', datetime.date(2017, 2, 12)),
                        ('no_date', None)],
                name='test_image')
def get_test_image(unsorted_tempdir: pl.Path, request):
    test_image_path = unsorted_tempdir / f'test_image_{request.param[0]}.jpeg'
    return {'path': test_image_path,
            'date': request.param[1]}


def test_get_image_date(test_image: dict):
    date = ps.get_file_date(test_image['path'])
    assert date == test_image['date']


def test_is_empty_dir(unsorted_tempdir):
    assert not ps.is_empty_dir(unsorted_tempdir)
    empty_dir = unsorted_tempdir / 'empty'
    empty_dir.mkdir()
    assert ps.is_empty_dir(empty_dir)


def test_sort_image(image_tempdir: pl.Path,
                    test_image: dict):
    new_path = ps.sort_file(test_image['path'], image_tempdir)
    date: datetime.date = test_image['date']
    if date:
        expected_path = (image_tempdir / date.strftime('%Y') / date.strftime('%Y-%m')
                         / date.strftime('%Y-%m-%d') / test_image['path'].name)
    else:
        expected_path = image_tempdir / 'Unknown' / test_image['path'].name
    assert new_path == expected_path
    assert ps.sort_file(new_path, image_tempdir) == new_path


def count_files(path: pl.Path, include_directories=False):
    dir_offset = 1 if include_directories else 0
    if path.is_dir():
        return sum(count_files(p, include_directories)
                   for p in path.iterdir()) + dir_offset
    else:
        return 1


def test_sort_directory(unsorted_tempdir: pl.Path, image_tempdir: pl.Path):
    ps.sort_directory(unsorted_tempdir, image_tempdir)
    assert count_files(image_tempdir) == 7
    assert count_files(image_tempdir, True) == 23

