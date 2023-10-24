"""core classes"""

import os
import arcpy

MAPS_EXCLUDE_PATTERN = ["template","00"]


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

    @property
    def maps(self):
        return _get_files_by_extension(self.path, ".mxd",exclude_patterns=MAPS_EXCLUDE_PATTERN)


    def export_all_maps(self, output_folder=None,verbose=False):
        for mxd in self.maps:
            if verbose:
                print("Exporting map: {}".format(mxd))
            with Map(mxd) as imap:
                imap.export_to_pdf()
            if verbose:
                print("Map exported: {}".format(mxd))

import fnmatch

def _get_files_by_extension(root, extension,exclude_patterns=None):
    files_list = []
    for root, subdirs, files in os.walk(root):
        for file in files:
            if file.endswith(extension):
                if exclude_patterns:
                    if any(pattern in file for pattern in exclude_patterns):
                        continue
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
            raise e