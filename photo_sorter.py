import os
import pathlib as pl
import datetime
import re
from typing import Union, TypeVar

from exifread import process_file

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
    sorted_files = set()
    directories_to_delete = set()
    for file in source_path.glob(glob_pattern):
        if file.name not in sorted_files:
            new_file = sort_file(file, target_path)
            if new_file:
                sorted_files.add(new_file)
            if remove_empty and is_empty_dir(file.parent):
                directories_to_delete.add(file.parent)
    for directory in directories_to_delete:
        if is_empty_dir(directory):
            directory.rmdir()


def sort_file(path: pl.Path, target_path: PathLike,
              ) -> Maybe[pl.Path]:
    if not isinstance(path, pl.Path):
        path = pl.Path(str(path))

    date = get_file_date(path)
    if date:
        new_path = (target_path / date.strftime('%Y') / date.strftime('%Y-%m')
                    / date.strftime('%Y-%m-%d') / path.name)
    else:
        new_path = target_path / 'Unknown' / path.name

    if new_path != path:
        if not new_path.parent.exists():
            new_path.parent.mkdir(parents=True)
        if new_path.exists():
            new_path = get_backup_path(new_path)
        path.rename(new_path)
    return new_path


def get_backup_path(path: pl.Path):
    def make_path(source_path: pl.Path, number: int):
        return source_path.with_name(
            f'{source_path.stem}_{number}.{source_path.suffix}')

    backup_count = 0
    new_path = make_path(path, backup_count)
    while new_path.exists():
        backup_count += 1
        new_path = make_path(path, backup_count)
    return new_path


def is_empty_dir(path: pl.Path):
    if path.is_dir():
        return sum(1 for _ in path.iterdir()) == 0
    else:
        return False


def get_file_date(path: pl.Path) -> Maybe[datetime.date]:
    return (get_file_date_from_metadata(path)
            or get_file_date_from_filename(path))


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


def get_file_date_from_mtime(path: pl.Path) -> Maybe[datetime.date]:
    return datetime.date.fromtimestamp(os.path.getmtime(path))


def load_tags(path: pl.Path) -> dict:
    with open(path, 'rb') as image_file:
        return process_file(image_file)
