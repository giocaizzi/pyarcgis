"""core classes"""

import os
import arcpy


class Project:
    _path = None

    def __init__(self, path):
        self.path = path

    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        self._path = os.path(path)


    def export_all_maps(self, output_folder=None,verbose=False):
        files = self._get_files_by_extension()
        for file in files:
            if verbose:
                print("Exporting map: {}".format(file))
            with Map(file) as imap:
                imap.export_to_pdf()
            if verbose:
                print("Map exported: {}".format(file))

    def _get_files_by_extension(self,extension = ".mxd"):
        files_list = []
        for root, subdirs, files in os.walk(self.path):
            for file in files:
                if file.endswith(extension):
                    files_list.append(os.path.join(root, file))
        return files_list


class Map:
    _mxd_path = None
    _map = None

    # must be used with a context manager

    def __init__(self, mxd_path):
        if not mxd_path.endswith(".mxd"):
            raise AttributeError("The path must be a .mxd file")
        self._mxd_path = mxd_path
        self._mxd_filename = os.path.basename(mxd_path)
        self._mxd_folder = os.path.dirname(mxd_path)
        self._map = arcpy.mapping.MapDocument(self._mxd_path)

    def __enter__(self):
        return self
    
    def __exit__(self):
        # Clean up the MapDocument object by deleting it.
        del self._map


    def export_to_pdf(self):
        try :
            arcpy.mapping.ExportToPDF(
                self._map,
                os.path.join(self._mxd_folder, self._mxd_filename+".pdf"))
        except Exception as e:
            print("Error exporting map: {}".format(self._mxd_path))
            print(e)