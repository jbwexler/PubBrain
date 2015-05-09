import os
import itertools
from django.core.files.storage import FileSystemStorage
from PubBrain import settings
from django.db.models import get_model
from fnmatch import fnmatch


class NiftiGzStorage(FileSystemStorage):

    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        return super(NiftiGzStorage, self).__init__(location, base_url)

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        if file_ext.lower() == ".gz":
            file_root2, file_ext2 = os.path.splitext(file_root)
            if file_ext2.lower() == ".nii":
                file_root = file_root2
                file_ext = file_ext2 + file_ext
        # If the filename already exists, add an underscore and a number (before
        # the file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(dir_name, "%s_%s%s" % (file_root, next(count), file_ext))

        return name

    def url(self, name):
        spath,file_name = os.path.split(name)
        urlsects = [v for v in spath.split('/') if v]
        cont_path = '/'.join(urlsects)
        return os.path.join(self.base_url,cont_path,file_name)

