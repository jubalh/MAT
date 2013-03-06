import parser
import shutil


class MutagenStripper(parser.GenericParser):
    def __init__(self, filename, parser, mime, backup, **kwargs):
        super(MutagenStripper, self).__init__(filename, parser, mime, backup, **kwargs)
        self._create_mfile()

    def _create_mfile(self):
        raise NotImplemented

    def is_clean(self):
        return not self.mfile.tags

    def remove_all(self):
        if self.backup:
            shutil.copy2(self.filename, self.output)
            self.mfile.filename = self.output
        else:
            self.mfile.filename = self.filename

        self.mfile.delete()
        self.mfile.save()
        return True

    def get_meta(self):
        '''
            Return the content of the metadata block is present
        '''
        metadata = {}
        if self.mfile.tags:
            for key, value in self.mfile.tags:
                metadata[key] = value
        return metadata
