"""core classes"""

import os
import arcpy

MAPS_EXCLUDE_PATTERN = ["template","00"]

LAYOUT_TEXT_ELEMENTS = [
    r"{{PROJ}}"
    ]

def _get_files_by_extension(root, extension, exclude_patterns=None, subset_pattern=None):
    if exclude_patterns and not isinstance(exclude_patterns, list):
        exclude_patterns = [exclude_patterns]
    if subset_pattern and not isinstance(subset_pattern, list):
        subset_pattern = [subset_pattern]
    files_list = []
    for root, subdirs, files in os.walk(root):
        for file in files:
            if file.endswith(extension):
                if exclude_patterns:
                    if any(pattern in file for pattern in exclude_patterns):
                        continue
                if subset_pattern is None or any(pattern in file for pattern in subset_pattern):
                    files_list.append(os.path.join(root, file))
    return files_list


class Project:
    _path = None

    def __init__(self, path):
        self._path = path
     
    @property
    def path(self):
        return self._path

    
    def get_maps(self,subset_pattern=None):
        return _get_files_by_extension(self.path, ".mxd",exclude_patterns=MAPS_EXCLUDE_PATTERN,subset_pattern=subset_pattern)


    def export_maps(self,maps,verbose=False):
        for mxd in maps:
            if verbose:
                print("Exporting map: {}".format(mxd))
            with Map(mxd) as imap:
                imap.export_to_pdf()
            if verbose:
                print("Map exported: {}".format(mxd))


class Map:
    _mxd_path = None
    _mxd_basename = None
    _mxd_filename = None
    _mxd_folder = None
    _map = None

    # must be used with a context manager to ensure the MapDocument object is deleted
    # after use (close the file)

    def __init__(self, mxd_path,save_on_exit=False):
        if not mxd_path.endswith(".mxd"):
            raise AttributeError("The path must be a .mxd file")
        self._mxd_path = mxd_path
        self._mxd_basename = os.path.basename(mxd_path)
        self._mxd_filename, _ = os.path.splitext(self._mxd_basename)
        self._mxd_folder = os.path.dirname(mxd_path)
        self._map = arcpy.mapping.MapDocument(self._mxd_path)
        self._save_on_exit = save_on_exit

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Clean up the MapDocument object by deleting it.
        if self._save_on_exit:
            self.save()
        del self._map

    def export_to_pdf(self):
        try :
            arcpy.mapping.ExportToPDF(
                self._map,
                os.path.join(self._mxd_folder, self._mxd_filename+".pdf"))
        except Exception as e:
            print("Error exporting map: {}".format(self._mxd_path))
            raise e
        
    def set_template_layout_text_elements(self,layout_elements_map):
        for element in LAYOUT_TEXT_ELEMENTS:
            self.set_text_element(element, layout_elements_map[element])
        
    def set_text_element(self, old_text, new_text):
        for element in self._get_layout_elements():
            if element.text == old_text:
                element.text = new_text

    
        

    def _get_layout_elements(self, element_type="TEXT_ELEMENT"):
        return arcpy.mapping.ListLayoutElements(self._map, element_type)
    
    def save(self):
        self._map.save()