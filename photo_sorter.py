import pathlib as p
import datetime

from exifread import process_file

sorted_files = set()


def sort_file(path: p.Path, base_path: p.Path) -> bool:
    if isinstance(path, str):
        path = p.Path(path)
    date = get_image_date(path)
    new_path = (base_path / date.strftime('%Y') / date.strftime('%Y-%m')
                / date.strftime('%Y-%m-%d') / path.name)
    if new_path != path:
        if not new_path.parent.exists():
            new_path.parent.mkdir(parents=True)
        make_backup(new_path)
        path.rename(new_path)
        if is_empty_dir(path.parent):
            path.parent.rmdir()
        return True
    else:
        return False



def make_backup(new_path):
    pass


def is_empty_dir(path: p.Path):
    if path.is_dir():
        return sum(1 for _ in path.iterdir()) == 0
    else:
        return False


def get_image_date(path: p.Path) -> datetime.date:
    date_tag_names = ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized',
                      'Image DateTime')
    tags = load_tags(path)
    for tag in date_tag_names:
        if tag in tags:
            date_str = tags[tag].values
            dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            return dt.date()
    else:
        raise ValueError(f'Unable to extract date from image {path!s}')


def load_tags(path: p.Path) -> dict:
    with open(path, 'rb') as image_file:
        return process_file(image_file)
