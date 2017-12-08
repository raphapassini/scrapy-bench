import tarfile


def extract_file_from_tar(tar_filename):
    tar = tarfile.open(tar_filename)
    for member in tar.getmembers():
        yield tar.extractfile(member)
