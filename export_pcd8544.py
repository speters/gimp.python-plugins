#!/usr/bin/env python

"""
GIMP plugin to export an image as a C header suitable for PCD8544 (Mokia 5110) LCD.

This code is released under the GPL license 
http://www.gnu.org/licenses/gpl.html

Thanks to Raul Aguaviva since this plugin is based on his KS108 export script
"""

import struct
import gimp
from gimpfu import *
import os
import re

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

# catch errors as suggested in http://www.gimptalk.com/index.php?/topic/53573-catch-errors-in-batch-mode/page__view__findpost__p__398824
def export_pcd8544(img, drawable, filename, raw_filename): 
    # pdb.gimp_image_undo_group_start(image)
    try:
        do_export_pcd8544(img, drawable, filename, raw_filename) 
    except Exception as e:
        print e.args[0]
        pdb.gimp_message(e.args[0])

    # pdb.gimp_image_undo_group_end(image)
    # pdb.gimp_displays_flush()  

def do_export_pcd8544(img, drawable, filename, raw_filename):
    pdb.gimp_layer_resize_to_image_size(drawable)
    gimp.pdb.gimp_message_set_handler( ERROR_CONSOLE )

    lcdwidth = 84
    lcdheight = 48
    lcdrows = 6
    rowpixels = lcdheight/lcdrows

    width = drawable.width
    height = drawable.height

    if (width < lcdwidth or height < lcdheight):
        raise Exception("Image too small (%dpx * %dpx, expected %dpx * %dpx)" % (width, height, lcdwidth, lcdheight)) 

    fileOut = open(filename,"w")

    #remove path from filename and extension
    filename = "".join([c for c in os.path.splitext(os.path.basename(filename))[0] if re.match(r'\w', c)])
    filename = "LCDIMAGE" if filename == "" else filename
        
    gimp.progress_init(_("Saving as PCD8544 C header (84x48x1)"))

    fileOut.write("#ifndef %s\n" % filename.upper() )
    fileOut.write("#define %s\n" % filename.upper() )
    fileOut.write("\n")
    fileOut.write("const uint8_t %s[] = {\n" % filename )

    index = 0
    # from https://github.com/adafruit/Adafruit_Nokia_LCD/blob/master/Adafruit_Nokia_LCD/PCD8544.py#L157
    for row in range(lcdrows):
        # Iterate through all 83 x axis columns.
        for x in range(lcdwidth):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                        (channels,pixel) = pdb.gimp_drawable_get_pixel(drawable, x, (row*rowpixels+7-bit))
                        bits = bits << 1
                        bits |= 1 if pixel[0] == 0 else 0
                        # Update buffer byte and increment to next byte.
                        index += 1
                fileOut.write("0x%02X%s" % (bits, ("" if (lcdwidth * lcdheight) == index  else ", ")))
        gimp.progress_update(float(index/(lcdwidth*lcdheight)))
        fileOut.write( "\n" )

    fileOut.write("};\n" )
    fileOut.write("#endif /* %s */\n" % filename.upper() )

    gimp.progress_update(1)
    fileOut.close()

def register_export_pcd8544():
    #  gimp.register_save_handler(name, extensions, prefixes)
    #  This procedure tells GIMP that the PDB procedure name can save files with extensions and prefixes (eg http:).
    gimp.register_save_handler("file-export_pcd8544", "h", "")

register(
        # name of the plugin
        proc_name = "file-export_pcd8544",
        # blurb, short piece of info about the plugin
        blurb = "C header for PCD8544 (Nokia 5110) LCD exporter",
        # help, a more detailed information
        help = "Export an image for the PCD8544 (Nokia 5110) LCD suitable for inclusion in C",
        # author
        author = "Soenke J. Peters",
        # copyright holder (usually the same as author)
        copyright = "Soenke J. Peters",
        # date when plugin was written
        date = "2014",
        # menu label (use menu parameter for full menu path)
        label = "C header for PCD8544 (NOKIA 5110) LCD",
        # imagetypes
        imagetypes = "INDEXED",
        # params
        params = [
            # (type, name, description, default [, extra])
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
            (PF_STRING, "filename", "The name of the file", None),
            (PF_STRING, "raw-filename", "The name of the file", None),
        ],
        # results
        results = [],
        # function
        function = export_pcd8544,
        menu = "<Image>/File/Export",
        on_query = register_export_pcd8544
        # on_run = None
)

main()
