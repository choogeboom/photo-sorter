import pathlib as pl
import datetime
import re
from typing import Union, TypeVar

from exifread import process_file

sorted_files = set()

PathLike = Union[str, bytes, pl.Path]
T = TypeVar('T')
Maybe = Union[T, None]


def sort_directory(source_path: pl.Path,
                   target_path: pl.Path,
                   remove_empty: bool=True,
                   recursive=True):
    assert source_path.is_dir()
    assert target_path.is_dir()
    if recursive:
        glob_pattern = '**/*.*'
    else:
        glob_pattern = '*.*'


def sort_file(path: pl.Path, target_path: PathLike,
              ) -> Maybe[pl.Path]:
    if not isinstance(path, pl.Path):
        path = pl.Path(str(path))
    date = get_file_date(path)
    if not date:
        return None
    new_path = (target_path / date.strftime('%Y') / date.strftime('%Y-%m')
                / date.strftime('%Y-%m-%d') / path.name)
    if new_path != path:
        if not new_path.parent.exists():
            new_path.parent.mkdir(parents=True)
        make_backup(new_path)
        path.rename(new_path)
        return new_path
    else:
        return None


def make_backup(new_path):
    pass


def is_empty_dir(path: pl.Path):
    if path.is_dir():
        return sum(1 for _ in path.iterdir()) == 0
    else:
        return False


def get_file_date(path: pl.Path) -> Maybe[datetime.date]:
    return (get_file_date_from_metadata(path)
            or get_file_date_from_filename(path)
            or get_file_date_from_properties(path))


def get_file_date_from_metadata(path: pl.Path) -> Maybe[datetime.date]:
    if path.suffix in ('jpg', 'jpeg'):
        date_tag_names = ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized',
                          'Image DateTime')
        tags = load_tags(path)
        for tag in date_tag_names:
            if tag in tags:
                date_str = tags[tag].values
                dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return dt.date()
    return None


def get_file_date_from_filename(path: pl.Path) -> Maybe[datetime.date]:
    pattern = r'(?P<year>\d{4})(.|\s+)?(?P<month>\d{2})(.|\s+)?(?P<day>\d{2})'
    match = re.search(pattern, path.name)
    if match:
        date_kwargs = {k: int(v) for k, v in match.groupdict().items()}
        return datetime.date(**date_kwargs)
    else:
        return None


def get_file_date_from_properties(path: pl.Path) -> Maybe[datetime.date]:
    return None


def load_tags(path: pl.Path) -> dict:
    with open(path, 'rb') as image_file:
        return process_file(image_file)
