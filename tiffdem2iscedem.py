#!/usr/bin/env python3

### some notes: only works with python3
### originally got error with importing module builtins
### fixed this by running: pip2 install future

import numpy as np
import argparse
from osgeo import gdal
import isce
import isceobj
import os

def cmdLineParse():
    """
    Parse command line.
    """
    parser = argparse.ArgumentParser(description='Convert GeoTiff to ISCE file')
    parser.add_argument('-i','--input', dest='infile', type=str, required=True, help='Input GeoTiff file. If tar file is also included, this will be output file extracted from the TAR archive.')
    parser.add_argument('-o','--output', dest='outfile', type=str, required=True, help='Output GeoTiff file')
    parser.add_argument('-t','--tar', dest='tarfile', type=str, default=None, help='Optional input tar archive. If provided, Band 8 is extracted to file name provided with input option.')
    return parser.parse_args()

def dumpTiff(infile, outfile):
    """
    Read geotiff tags.
    """
    ###Uses gdal bindings to read geotiff files
    data = {}
    ds = gdal.Open(infile)
    data['width'] = ds.RasterXSize
    data['length'] = ds.RasterYSize
    gt = ds.GetGeoTransform()
    data['minx'] = gt[0]
    data['miny'] = gt[3] + data['width'] * gt[4] + data['length']*gt[5]
    data['maxx'] = gt[0] + data['width'] * gt[1] + data['length']*gt[2]
    data['maxy'] = gt[3]
    data['deltax'] = gt[1]
    data['deltay'] = gt[5]
    data['reference'] = ds.GetProjectionRef()
    band = ds.GetRasterBand(1)
    inArr = band.ReadAsArray(0,0, data['width'], data['length'])
    inArr.astype(np.float32).tofile(outfile)
    return data


if __name__ == '__main__':
    ####Parse cmd line
    inps = cmdLineParse()
    ####If input tar file is given

    print('Dumping image to file')
    meta = dumpTiff(inps.infile, inps.outfile)
    # print(meta)
    ####Create an ISCE XML header for the landsat image
    img = isceobj.createDemImage()
    img.setFilename(inps.outfile)
    img.setDataType('FLOAT')
    dictProp = {
    'REFERENCE' : meta['reference'],
    'Coordinate1': {
    'size': meta['width'],
    'startingValue' : meta['minx'],
    'delta': meta['deltax']
    },
    'Coordinate2': {
    'size' : meta['length'],
    'startingValue' : meta['maxy'],
    'delta': meta['deltay']
    },
    'FILE_NAME' : inps.outfile
    }
    img.init(dictProp)
    img.renderHdr()
    
    
    
