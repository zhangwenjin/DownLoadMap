#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL2Tiles, Google Summer of Code 2007 & 2008
#           Global Map Tiles Classes
# Purpose:  Convert a raster into TMS tiles, create KML SuperOverlay EPSG:4326,
#           generate a simple HTML viewers based on Google Maps and OpenLayers
# Author:   Klokan Petr Pridal, klokan at klokan dot cz
# Web:      http://www.klokan.cz/projects/gdal2tiles/
#
###############################################################################
# Copyright (c) 2008 Klokan Petr Pridal. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

"""
globalmaptiles.py
37.Global Map Tiles as defined in Tile Map Service (TMS) Profiles
38.==============================================================
39.
40.Functions necessary for generation of global tiles used on the web.
41.It contains classes implementing coordinate conversions for:
42.
43.  - GlobalMercator (based on EPSG:900913 = EPSG:3785)
44.       for Google Maps, Yahoo Maps, Microsoft Maps compatible tiles
45.  - GlobalGeodetic (based on EPSG:4326)
46.       for OpenLayers Base Map and Google Earth compatible tiles
47.
48.More info at:
49.
50.http://wiki.osgeo.org/wiki/Tile_Map_Service_Specification
51.http://wiki.osgeo.org/wiki/WMS_Tiling_Client_Recommendation
52.http://msdn.microsoft.com/en-us/library/bb259689.aspx
53.http://code.google.com/apis/maps/documentation/overlays.html#Google_Maps_Coordinates
54.
55.Created by Klokan Petr Pridal on 2008-07-03.
56.Google Summer of Code 2008, project GDAL2Tiles for OSGEO.
57.
58.In case you use this class in your product, translate it to another language
59.or find it usefull for your project please let me know.
60.My email: klokan at klokan dot cz.
61.I would like to know where it was used.
62.
63.Class is available under the open-source GDAL license (www.gdal.org).
"""
import math

class GlobalMercator(object):
    """
70.    TMS Global Mercator Profile
71.    ---------------------------
72.
73.    Functions necessary for generation of tiles in Spherical Mercator projection,
74.    EPSG:900913 (EPSG:gOOglE, Google Maps Global Mercator), EPSG:3785, OSGEO:41001.
75.
76.    Such tiles are compatible with Google Maps, Microsoft Virtual Earth, Yahoo Maps,
77.    UK Ordnance Survey OpenSpace API, ...
78.    and you can overlay them on top of base maps of those web mapping applications.
79.
80.    Pixel and tile coordinates are in TMS notation (origin [0,0] in bottom-left).
81.
82.    What coordinate conversions do we need for TMS Global Mercator tiles::
83.
84.         LatLon      <->       Meters      <->     Pixels    <->       Tile
85.
86.     WGS84 coordinates   Spherical Mercator  Pixels in pyramid  Tiles in pyramid
87.         lat/lon            XY in metres     XY pixels Z zoom      XYZ from TMS
88.        EPSG:4326           EPSG:900913
89.         .----.              ---------               --                TMS
90.        /      \     <->     |       |     <->     /----/    <->      Google
91.        \      /             |       |           /--------/          QuadTree
92.         -----               ---------         /------------/
93.       KML, public         WebMapService         Web Clients      TileMapService
94.
95.    What is the coordinate extent of Earth in EPSG:900913?
96.
97.      [-20037508.342789244, -20037508.342789244, 20037508.342789244, 20037508.342789244]
98.      Constant 20037508.342789244 comes from the circumference of the Earth in meters,
99.      which is 40 thousand kilometers, the coordinate origin is in the middle of extent.
100.      In fact you can calculate the constant as: 2 * math.pi * 6378137 / 2.0
101.      $ echo 180 85 | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:900913
102.      Polar areas with abs(latitude) bigger then 85.05112878 are clipped off.
103.
104.    What are zoom level constants (pixels/meter) for pyramid with EPSG:900913?
105.
106.      whole region is on top of pyramid (zoom=0) covered by 256x256 pixels tile,
107.      every lower zoom level resolution is always divided by two
108.      initialResolution = 20037508.342789244 * 2 / 256 = 156543.03392804062
109.
110.    What is the difference between TMS and Google Maps/QuadTree tile name convention?
111.
112.      The tile raster itself is the same (equal extent, projection, pixel size),
113.      there is just different identification of the same raster tile.
114.      Tiles in TMS are counted from [0,0] in the bottom-left corner, id is XYZ.
115.      Google placed the origin [0,0] to the top-left corner, reference is XYZ.
116.      Microsoft is referencing tiles by a QuadTree name, defined on the website:
117.      http://msdn2.microsoft.com/en-us/library/bb259689.aspx
118.
119.    The lat/lon coordinates are using WGS84 datum, yeh?
120.
121.      Yes, all lat/lon we are mentioning should use WGS84 Geodetic Datum.
122.      Well, the web clients like Google Maps are projecting those coordinates by
123.      Spherical Mercator, so in fact lat/lon coordinates on sphere are treated as if
124.      the were on the WGS84 ellipsoid.
125.
126.      From MSDN documentation:
127.      To simplify the calculations, we use the spherical form of projection, not
128.      the ellipsoidal form. Since the projection is used only for map display,
129.      and not for displaying numeric coordinates, we don't need the extra precision
130.      of an ellipsoidal projection. The spherical projection causes approximately
131.      0.33 percent scale distortion in the Y direction, which is not visually noticable.
132.
133.    How do I create a raster in EPSG:900913 and convert coordinates with PROJ.4?
134.
135.      You can use standard GIS tools like gdalwarp, cs2cs or gdaltransform.
136.      All of the tools supports -t_srs 'epsg:900913'.
137.
138.      For other GIS programs check the exact definition of the projection:
139.      More info at http://spatialreference.org/ref/user/google-projection/
140.      The same projection is degined as EPSG:3785. WKT definition is in the official
141.      EPSG database.
142.
143.      Proj4 Text:
144.        +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0
145.        +k=1.0 +units=m +nadgrids=@null +no_defs
146.
147.      Human readable WKT format of EPGS:900913:
148.         PROJCS["Google Maps Global Mercator",
149.             GEOGCS["WGS 84",
150.                 DATUM["WGS_1984",
151.                     SPHEROID["WGS 84",6378137,298.2572235630016,
152.                         AUTHORITY["EPSG","7030"]],
153.                     AUTHORITY["EPSG","6326"]],
154.                 PRIMEM["Greenwich",0],
155.                 UNIT["degree",0.0174532925199433],
156.                 AUTHORITY["EPSG","4326"]],
157.             PROJECTION["Mercator_1SP"],
158.             PARAMETER["central_meridian",0],
159.             PARAMETER["scale_factor",1],
160.             PARAMETER["false_easting",0],
161.             PARAMETER["false_northing",0],
162.             UNIT["metre",1,
163.                 AUTHORITY["EPSG","9001"]]]
164.    """
    def __init__(self, tileSize=256):
        "Initialize the TMS Global Mercator pyramid"
        self.tileSize = tileSize
        self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
        # 156543.03392804062 for tileSize 256 pixels
        self.originShift = 2 * math.pi * 6378137 / 2.0
        # 20037508.342789244

    def LatLonToMeters(self, lat, lon ):
        "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"

        mx = lon * self.originShift / 180.0
        my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)

        my = my * self.originShift / 180.0
        return mx, my

    def MetersToLatLon(self, mx, my ):
        "Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum"

        lon = (mx / self.originShift) * 180.0
        lat = (my / self.originShift) * 180.0

        lat = 180 / math.pi * (2 * math.atan( math.exp( lat * math.pi / 180.0)) - math.pi / 2.0)
        return lat, lon

    def PixelsToMeters(self, px, py, zoom):
        "Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"

        res = self.Resolution( zoom )
        mx = px * res - self.originShift
        my = py * res - self.originShift
        return mx, my

    def MetersToPixels(self, mx, my, zoom):
        "Converts EPSG:900913 to pyramid pixel coordinates in given zoom level"

        res = self.Resolution( zoom )
        px = (mx + self.originShift) / res
        py = (my + self.originShift) / res
        return px, py

    def PixelsToTile(self, px, py):
        "Returns a tile covering region in given pixel coordinates"

        tx = int( math.ceil( px / float(self.tileSize) ) - 1 )
        ty = int( math.ceil( py / float(self.tileSize) ) - 1 )
        return tx, ty

    def PixelsToRaster(self, px, py, zoom):
        "Move the origin of pixel coordinates to top-left corner"

        mapSize = self.tileSize << zoom
        return px, mapSize - py

    def MetersToTile(self, mx, my, zoom):
        "Returns tile for given mercator coordinates"

        px, py = self.MetersToPixels( mx, my, zoom)
        return self.PixelsToTile( px, py)

    def TileBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile in EPSG:900913 coordinates"

        minx, miny = self.PixelsToMeters( tx*self.tileSize, ty*self.tileSize, zoom )
        maxx, maxy = self.PixelsToMeters( (tx+1)*self.tileSize, (ty+1)*self.tileSize, zoom )
        return ( minx, miny, maxx, maxy )

    def TileLatLonBounds(self, tx, ty, zoom ):
        "Returns bounds of the given tile in latutude/longitude using WGS84 datum"

        bounds = self.TileBounds( tx, ty, zoom)
        minLat, minLon = self.MetersToLatLon(bounds[0], bounds[1])
        maxLat, maxLon = self.MetersToLatLon(bounds[2], bounds[3])

        return ( minLat, minLon, maxLat, maxLon )

    def Resolution(self, zoom ):
        "Resolution (meters/pixel) for given zoom level (measured at Equator)"

        # return (2 * math.pi * 6378137) / (self.tileSize * 2**zoom)
        return self.initialResolution / (2**zoom)

    def ZoomForPixelSize(self, pixelSize ):
        "Maximal scaledown zoom of the pyramid closest to the pixelSize."

        for i in range(30):
            if pixelSize > self.Resolution(i):
                return i-1 if i!=0 else 0 # We don't want to scale up

    def GoogleTile(self, tx, ty, zoom):
        "Converts TMS tile coordinates to Google Tile coordinates"

        # coordinate origin is moved from bottom-left to top-left corner of the extent
        return tx, (2**zoom - 1) - ty

    def QuadTree(self, tx, ty, zoom ):
        "Converts TMS tile coordinates to Microsoft QuadTree"

        quadKey = ""
        ty = (2**zoom - 1) - ty
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i-1)
            if (tx & mask) != 0:
                digit += 1
            if (ty & mask) != 0:
                digit += 2
            quadKey += str(digit)

        return quadKey

#---------------------

class GlobalGeodetic(object):
    """
282.    TMS Global Geodetic Profile
283.    ---------------------------
284.
285.    Functions necessary for generation of global tiles in Plate Carre projection,
286.    EPSG:4326, "unprojected profile".
287.
288.    Such tiles are compatible with Google Earth (as any other EPSG:4326 rasters)
289.    and you can overlay the tiles on top of OpenLayers base map.
290.
291.    Pixel and tile coordinates are in TMS notation (origin [0,0] in bottom-left).
292.
293.    What coordinate conversions do we need for TMS Global Geodetic tiles?
294.
295.      Global Geodetic tiles are using geodetic coordinates (latitude,longitude)
296.      directly as planar coordinates XY (it is also called Unprojected or Plate
297.      Carre). We need only scaling to pixel pyramid and cutting to tiles.
298.      Pyramid has on top level two tiles, so it is not square but rectangle.
299.      Area [-180,-90,180,90] is scaled to 512x256 pixels.
300.      TMS has coordinate origin (for pixels and tiles) in bottom-left corner.
301.      Rasters are in EPSG:4326 and therefore are compatible with Google Earth.
302.
303.         LatLon      <->      Pixels      <->     Tiles
304.
305.     WGS84 coordinates   Pixels in pyramid  Tiles in pyramid
306.         lat/lon         XY pixels Z zoom      XYZ from TMS
307.        EPSG:4326
308.         .----.                ----
309.        /      \     <->    /--------/    <->      TMS
310.        \      /         /--------------/
311.         -----        /--------------------/
312.       WMS, KML    Web Clients, Google Earth  TileMapService
313.    """

    def __init__(self, tileSize = 256):
        self.tileSize = tileSize

    def LatLonToPixels(self, lat, lon, zoom):
        "Converts lat/lon to pixel coordinates in given zoom of the EPSG:4326 pyramid"

        res = 180 / 256.0 / 2**zoom
        px = (180 + lat) / res
        py = (90 + lon) / res
        return px, py

    def PixelsToTile(self, px, py):
        "Returns coordinates of the tile covering region in pixel coordinates"

        tx = int( math.ceil( px / float(self.tileSize) ) - 1 )
        ty = int( math.ceil( py / float(self.tileSize) ) - 1 )
        return tx, ty

    def Resolution(self, zoom ):
        "Resolution (arc/pixel) for given zoom level (measured at Equator)"

        return 180 / 256.0 / 2**zoom
        #return 180 / float( 1 << (8+zoom) )

    def TileBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile"
        res = 180 / 256.0 / 2**zoom
        return (
            tx*256*res - 180,
            ty*256*res - 90,
            (tx+1)*256*res - 180,
            (ty+1)*256*res - 90
        )

if __name__ == "__main__":
    import sys, os

    def Usage(s = ""):
        print "Usage: globalmaptiles.py [-profile 'mercator'|'geodetic'] zoomlevel lat lon [latmax lonmax]"
        print
        if s:
            print s
            print
        print "This utility prints for given WGS84 lat/lon coordinates (or bounding box) the list of tiles"
        print "covering specified area. Tiles are in the given 'profile' (default is Google Maps 'mercator')"
        print "and in the given pyramid 'zoomlevel'."
        print "For each tile several information is printed including bonding box in EPSG:900913 and WGS84."
        sys.exit(1)

    profile = 'mercator'
    zoomlevel = None
    lat, lon, latmax, lonmax = None, None, None, None
    boundingbox = False

    argv = sys.argv
    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == '-profile':
            i = i + 1
            profile = argv[i]

        if zoomlevel is None:
            zoomlevel = int(argv[i])
        elif lat is None:
            lat = float(argv[i])
        elif lon is None:
            lon = float(argv[i])
        elif latmax is None:
            latmax = float(argv[i])
        elif lonmax is None:
            lonmax = float(argv[i])
        else:
            Usage("ERROR: Too many parameters")

        i = i + 1

    if profile != 'mercator':
        Usage("ERROR: Sorry, given profile is not implemented yet.")

    if zoomlevel == None or lat == None or lon == None:
        Usage("ERROR: Specify at least 'zoomlevel', 'lat' and 'lon'.")
    if latmax is not None and lonmax is None:
        Usage("ERROR: Both 'latmax' and 'lonmax' must be given.")

    if latmax != None and lonmax != None:
        if latmax < lat:
            Usage("ERROR: 'latmax' must be bigger then 'lat'")
        if lonmax < lon:
            Usage("ERROR: 'lonmax' must be bigger then 'lon'")
        boundingbox = (lon, lat, lonmax, latmax)

    tz = zoomlevel
    mercator = GlobalMercator()

    mx, my = mercator.LatLonToMeters( lat, lon )
    print "Spherical Mercator (ESPG:900913) coordinates for lat/lon: "
    print (mx, my)
    tminx, tminy = mercator.MetersToTile( mx, my, tz )

    if boundingbox:
        mx, my = mercator.LatLonToMeters( latmax, lonmax )
        print "Spherical Mercator (ESPG:900913) cooridnate for maxlat/maxlon: "
        print (mx, my)
        tmaxx, tmaxy = mercator.MetersToTile( mx, my, tz )
    else:
        tmaxx, tmaxy = tminx, tminy

    for ty in range(tminy, tmaxy+1):
        for tx in range(tminx, tmaxx+1):
            tilefilename = "%s/%s/%s" % (tz, tx, ty)
            print tilefilename, "( TileMapService: z / x / y )"

            gx, gy = mercator.GoogleTile(tx, ty, tz)
            print "\tGoogle:", gx, gy
            quadkey = mercator.QuadTree(tx, ty, tz)
            print "\tQuadkey:", quadkey, '(',int(quadkey, 4),')'
            bounds = mercator.TileBounds( tx, ty, tz)
            print "\tEPSG:900913 Extent: ", bounds
            wgsbounds = mercator.TileLatLonBounds( tx, ty, tz)
            print "\tWGS84 Extent:", wgsbounds
            print "\tgdalwarp -ts 256 256 -te %s %s %s %s %s %s_%s_%s.tif" % (
                bounds[0], bounds[1], bounds[2], bounds[3], "<your-raster-file-in-epsg900913.ext>", tz, tx, ty)

