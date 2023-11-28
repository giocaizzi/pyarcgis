"""core classes"""

import os
import arcpy
from contextlib import contextmanager

MAPS_EXCLUDE_PATTERN = ["template","00"]

def _get_files_by_extension(root, extension, exclude_patterns=None, subset_pattern=None):
    """get files by extension in a root folder
    
    has filtering capabilities to exclude and include files with specific patterns in their name
    """
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

@contextmanager
def verbose_operation(before_msg, after_msg, verbose):
    """context manager for verbose operations"""
    try:
        if verbose:
            print(before_msg)
        yield
    finally:
        if verbose:
            print(after_msg)

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
            with verbose_operation("Exporting map: {}".format(mxd), "Map exported!", verbose):
                with Map(mxd) as imap:
                    imap.export_to_pdf()

    def set_layout_text_elements(self, maps, text_elements_map, verbose=False):
        for mxd in maps:
            with verbose_operation(
                "Setting layout text elements: {}".format(mxd),
                "Layout text elements set and saved!", verbose
                ):
                # required to savethe changes
                with Map(mxd, save_on_exit=True) as imap:
                    imap.set_layout_text_elements(text_elements_map)

    

class Map:
    """Map class
    
    Represents a mxd file with its Layout and DataFrames.

    Parameters
    ----------
    mxd_path : str
        The path to the mxd file.
    save_on_exit : bool, optional
        If True, the mxd file will be saved on exit. The default is False.
    """
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
    
    def save(self):
        """save the map"""
        self._map.save()

    @property
    def filename(self):
        """get filename of the mxd file"""
        return self._mxd_filename
    
    @property
    def map_object(self):
        """get the arcpy map object"""
        return self._map

    @property
    def dataframes(self):
        """get list of dataframes"""
        return arcpy.mapping.ListDataFrames(self.map_object)

    def __enter__(self):
        # context manager enter method
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # context manager exit method
        # Clean up the MapDocument object by deleting it.
        if self._save_on_exit:
            self.save()
        del self._map

    def export_to_pdf(self):
        """export the map to a pdf file"""
        # export the map to a pdf file
        try :
            arcpy.mapping.ExportToPDF(
                self.map_object,
                os.path.join(self._mxd_folder, self.filename+".pdf"))
        except Exception as e:
            print("Error exporting map: {}".format(self._mxd_path))
            raise e

    def set_layout_text_elements(self,layout_elements_map):
        """set layout text elements passed with a map to new text"""
        # set template layout text elements
        for key in layout_elements_map:
            self._set_layout_text_element(key, layout_elements_map[key])

    def set_extent(self,dataframe_name=None,xmin=None,xmax=None,ymin=None,ymax=None,extent=None):
        """set extent of a specific dataframe by passing xmin,xmax,ymin,ymax or an arcpy.Extent object"""
        # check if the user passed the correct parameters
        point_extent = (xmin is not None and xmax is not None and ymin is not None and ymax is not None)
        extent_extent = (extent is not None)
        if point_extent and extent_extent:
            raise Exception("You can't pass both point extent and extent object")
        if not point_extent and not extent_extent:
            raise Exception("You must pass either point extent or extent object")
        
        # if only one dataframe no need to pass the dataframe name
        if len(self.dataframes) == 1:
            dataframe_name = self.dataframes[0].name
        else:
            if dataframe_name is None:
                raise Exception("You must pass a dataframe name")

        # set extent
        if point_extent:
            for df in self.dataframes:
                if df.name == dataframe_name:
                    df.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
                    break
                raise Exception("dataframe not found")

        else:
            for df in self.dataframes:
                if df.name == dataframe_name:
                    df.extent = arcpy.Extent(extent.XMin,extent.YMin,extent.XMax,extent.YMax)
                    break
                raise Exception("dataframe not found")
        
        # check that the extent is set correctly
        if point_extent:
            for df in self.dataframes:
                if df.name == dataframe_name:
                    if df.extent.XMin != xmin or df.extent.XMax != xmax or df.extent.YMin != ymin or df.extent.YMax != ymax:
                        raise Exception("Extent not set correctly")
        if extent_extent:
            for df in self.dataframes:
                if df.name == dataframe_name:
                    if df.extent.XMin != extent.XMin or df.extent.XMax != extent.XMax or df.extent.YMin != extent.YMin or df.extent.YMax != extent.YMax:
                        raise Exception("Extent not set correctly")

        
        # set view to pagelayout before exiting 
        # to avoid weird behaviour if view is model after
        # having set extent
        self.map_object.activeView = "PAGE_LAYOUT"


    def _get_layout_elements(self, element_type="TEXT_ELEMENT"):
        """get layout elements of a specific type"""
        return arcpy.mapping.ListLayoutElements(self.map_object, element_type)

    def _set_layout_text_element(self, old_text, new_text):
        """set text element to new text"""
        # set text element
        for element in self._get_layout_elements():
            if element.text == old_text:
                element.text = new_text
                break
        else:
            raise Exception("Text element not found: {}".format(old_text))


