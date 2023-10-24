import arcpy, os
folderPath = r"C:\Users\GIORGIO.CAIZZI\AECOM\60674684ER Taurasi1 Report di indagine - 09_Temp"
for filename in os.listdir(folderPath):
    fullpath = os.path.join(folderPath, filename)
    if os.path.isfile(fullpath):
        basename, extension = os.path.splitext(fullpath)
        if extension.lower() == ".mxd":
            mxd = arcpy.mapping.MapDocument(fullpath)
            arcpy.mapping.ExportToPDF(mxd, basename + '.pdf')
            del mxd