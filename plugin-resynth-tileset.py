#!/usr/bin/env python

# Gimp plugin for generating tilesets
# See README for more information

# Copyright (C) 2013 Adam Newgas
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gimpenums
import collections

import gimp
pdb = gimp.pdb

Tile = collections.namedtuple("Tile","top right bottom left")

# Enumerate the possible borders a tile can have
BLANK=0
SOLID=1
LEFT=2# For "top", otherwise rotate
RIGHT=3# ditto
BOTH=4# ditto

# Bit of a special case, but it doesn't fit into
# the border naming system
EMPTY_TILE=None
# Lists all combinations of possible tiles, in an aesthetic
# arrangement.
# See http://www.squidi.net/mapmaker/musings/m091016.php
tiles = {
    EMPTY_TILE: (0, 4),
    Tile(BLANK,BLANK,BOTH,BLANK): (0,0),
    Tile(BOTH,BLANK,BOTH,BLANK): (0,1),
    Tile(BOTH,BLANK,BLANK,BLANK): (0,2),
    Tile(BLANK,LEFT,RIGHT,BLANK): (1,0),
    Tile(LEFT,SOLID,RIGHT,BLANK): (1,1),
    Tile(LEFT,RIGHT,BLANK,BLANK): (1,2),
    Tile(BLANK,BOTH,BLANK,BLANK): (1,3),
    Tile(BLANK,LEFT,SOLID,RIGHT): (2,0),
    Tile(SOLID,SOLID,SOLID,SOLID): (2,1),
    Tile(SOLID,RIGHT,BLANK,LEFT): (2,2),
    Tile(BLANK,BOTH,BLANK,BOTH): (2,3),
    Tile(RIGHT,LEFT,RIGHT,LEFT): (2,4),
    Tile(BLANK,BLANK,LEFT,RIGHT): (3,0),
    Tile(RIGHT,BLANK,LEFT,SOLID): (3,1),
    Tile(RIGHT,BLANK,BLANK,LEFT): (3,2),
    Tile(BLANK,BLANK,BLANK,BOTH): (3,3),
    Tile(LEFT,RIGHT,LEFT,RIGHT): (3,4),
    Tile(BLANK,BOTH,BOTH,BLANK): (4,0),
    Tile(BOTH,BOTH,BOTH,BLANK): (4,1),
    Tile(BOTH,BOTH,BLANK,BLANK): (4,2),
    Tile(BLANK,BOTH,LEFT,RIGHT): (4,3),
    Tile(BOTH,LEFT,RIGHT,BLANK): (4,4),
    Tile(BLANK,BOTH,BOTH,BOTH): (5,0),
    Tile(BLANK,BLANK,BLANK,BLANK): (5,1),
    Tile(BOTH,BOTH,BLANK,BOTH): (5,2),
    Tile(RIGHT,BLANK,BOTH,LEFT): (5,3),
    Tile(LEFT,RIGHT,BLANK,BOTH): (5,4),
    Tile(BLANK,BLANK,BOTH,BOTH): (6,0),
    Tile(BOTH,BLANK,BOTH,BOTH): (6,1),
    Tile(BOTH,BLANK,BLANK,BOTH): (6,2),
    Tile(LEFT,RIGHT,BOTH,BLANK): (6,3),
    Tile(RIGHT,BOTH,BLANK,LEFT): (6,4),
    Tile(SOLID,RIGHT,LEFT,SOLID): (7,0),
    Tile(RIGHT,BOTH,LEFT,SOLID): (7,1),
    Tile(RIGHT,LEFT,SOLID,SOLID): (7,2),
    Tile(BLANK,LEFT,RIGHT,BOTH): (7,3),
    Tile(BOTH,BLANK,LEFT,RIGHT): (7,4),
    Tile(SOLID,RIGHT,BOTH,LEFT): (8,0),
    Tile(BOTH,BOTH,BOTH,BOTH): (8,1),
    Tile(BOTH,LEFT,SOLID,RIGHT): (8,2),
    Tile(RIGHT,BOTH,BOTH,LEFT): (8,3),
    Tile(BOTH,BOTH,LEFT,RIGHT): (8,4),
    Tile(SOLID,SOLID,RIGHT,LEFT): (9,0),
    Tile(LEFT,SOLID,RIGHT,BOTH): (9,1),
    Tile(LEFT,SOLID,SOLID,RIGHT): (9,2),
    Tile(LEFT,RIGHT,BOTH,BOTH): (9,3),
    Tile(BOTH,LEFT,RIGHT,BOTH): (9,4),
    }

def draw_rect(l,x,y,w,h,color):
    pdb.gimp_image_select_rectangle(l.image,
                                    gimpenums.CHANNEL_OP_REPLACE,x,y,w,h)
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)

def make_blob_output_pattern(tile_width, inset, outer_radius, inner_radius):
    w = tile_width
    h=w
    inner_radius = min(inner_radius, inset)
    outer_radius = min(outer_radius, (w-2*inset) / 2.0 )
    img = gimp.Image(10*w,5*h,gimpenums.GRAY)
    l = gimp.Layer(img, "Base", img.width,img.height,gimpenums.GRAY_IMAGE,100,
                   gimpenums.NORMAL_MODE)
    img.add_layer(l)
    def get_range(face, face_type):
        if face_type == BLANK: return None
        if face_type == LEFT: r = (inset,w-inset)
        if face_type == SOLID: r = (0,w)
        if face_type == RIGHT: r = (0, w-inset)
        if face_type == BOTH: r = (inset, w-inset*2)
        if face == "top": r = (r[0],0,r[1],inset)
        if face == "right": r = (w-inset,r[0],inset,r[1])
        if face == "bottom": r = (w-r[0]-r[1],w-inset,r[1],inset)
        if face == "left": r = (0,w-r[0]-r[1],inset,r[1])
        return r
    for tile, pos in tiles.items():
        if tile is None: continue
        x = pos[0]*w
        y = pos[1]*w
        color = ((pos[0]+pos[1])%2)*100+100
        color = (color,color,color)
        color = (255,255,255)
        pdb.gimp_context_set_foreground(color)
        pdb.gimp_context_set_background((0,0,0))
        # Draw the center of the filled tile
        cx = x+w/2.0
        cy = y+h/2.0
        b = (w-2*inset)/2.0
        draw_rect(l,x+inset,y+inset,w-2*inset,h-2*inset,color)
        if outer_radius > 0:
            if tile.top == BLANK and tile.left == BLANK:
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, cx-b,cy-b,outer_radius,outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,cx-b,cy-b,2*outer_radius,2*outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
            if tile.top == BLANK and tile.right == BLANK:
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, cx+b-outer_radius,cy-b,outer_radius,outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,cx+b-2*outer_radius,cy-b,2*outer_radius,2*outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
            if tile.bottom == BLANK and tile.right == BLANK:
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, cx+b-outer_radius,cy+b-outer_radius,outer_radius,outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,cx+b-2*outer_radius,cy+b-outer_radius*2,2*outer_radius,2*outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
            if tile.bottom == BLANK and tile.left == BLANK:
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, cx-b,cy+b-outer_radius,outer_radius,outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,cx-b,cy+b-outer_radius*2,2*outer_radius,2*outer_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
        # Connect the center to the edge
        for i, face in enumerate(("top","right","bottom","left")):
            t = getattr(tile, face)
            r = get_range(face, t)
            if r is None: continue
            draw_rect(l, x+r[0],y+r[1],r[2],r[3], color)
        # Draw the inner corners
        if inner_radius > 0:
            def is_corner(t1, t2):
                return (t1==BOTH or t1==RIGHT) and (t2==BOTH or t2==LEFT)
            if is_corner(tile.left, tile.top):
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x,y,inset,inset)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+inset-inner_radius,y+inset-inner_radius,inner_radius,inner_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,x+inset-inner_radius*2,y+inset-inner_radius*2,inner_radius*2,inner_radius*2)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
            if is_corner(tile.top, tile.right):
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+w-inset,y,inset,inset)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+w-inset,y+inset-inner_radius,inner_radius,inner_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,x+w-inset,y+inset-inner_radius*2,inner_radius*2,inner_radius*2)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
            if is_corner(tile.right, tile.bottom):
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+w-inset,y+h-inset,inset,inset)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+w-inset,y+h-inset,inner_radius,inner_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,x+w-inset,y+h-inset,inner_radius*2,inner_radius*2)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
            if is_corner(tile.bottom, tile.left):
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x,y+h-inset,inset,inset)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
                pdb.gimp_image_select_rectangle(img, gimpenums.CHANNEL_OP_REPLACE, x+inset-inner_radius,y+h-inset,inner_radius,inner_radius)
                pdb.gimp_edit_fill(l, gimpenums.FOREGROUND_FILL)
                pdb.gimp_image_select_ellipse(img, gimpenums.CHANNEL_OP_INTERSECT,x+inset-inner_radius*2,y+h-inset,inner_radius*2,inner_radius*2)
                pdb.gimp_edit_fill(l, gimpenums.BACKGROUND_FILL)
    pdb.gimp_selection_none(img)
    d = gimp.Display(img)

def make_blob_output(source, source_map, output_map, map_weight, autism, neighbourhood, trys):
    w = int(output_map.width / 10)
    assert w*10 == output_map.width
    assert w*5 == output_map.height
    def copy_tile(src, src_x, src_y, dest, dest_x, dest_y):
        pdb.gimp_image_select_rectangle(src.image, gimpenums.CHANNEL_OP_REPLACE,
                                        src_x*w,src_y*w,w,w)
        pdb.gimp_edit_copy(src)
        l = pdb.gimp_edit_paste(dest, 0)
        l.set_offsets(dest_x*w, dest_y*w)
        pdb.gimp_floating_sel_anchor(l)
    result = gimp.Image(w*10,w*5)
    result_layer = gimp.Layer(result, "Result", result.width, result.height)
    result.add_layer(result_layer)
    # Give the user something to look at while we're working
    # The resynthesis is slow enough there's little to be gained from
    # not updating the UI
    result_display = gimp.Display(result)
    # These special tiles are the first ones to be synthesized
    # and are used as the seed for generating others
    SOLID_TILE = Tile(SOLID,SOLID,SOLID,SOLID)
    HORIZ_TILE = Tile(BLANK,BOTH,BLANK,BOTH)
    TL_TILE = Tile(BLANK,LEFT,RIGHT,BLANK)
    TR_TILE=Tile(BLANK,BLANK,LEFT,RIGHT)
    BL_TILE=Tile(LEFT,RIGHT,BLANK,BLANK)
    BR_TILE=Tile(RIGHT,BLANK,BLANK,LEFT)
    VERT_TILE = Tile(BOTH,BLANK,BOTH,BLANK)

    result_dict = {}
    # Creates a temporary image with tiles given in the 2d array
    # If a tile is missing, it is an indication it needs to be synthesized
    def synth_image(a, tile_horiz=False, tile_vert=False, show=False):
        a_width = max(len(row) for row in a)
        a_height = len(a)
        i = gimp.Image(a_width*w, a_height*w)
        l = gimp.Layer(i, "Base", i.width, i.height)
        i.add_layer(l)
        mi = gimp.Image(i.width,i.height,gimpenums.GRAY)
        m = gimp.Layer(mi, "Mask", mi.width, mi.height,gimpenums.GRAY_IMAGE)
        mi.add_layer(m)
        # Copy up tiles that we have, and mask
        for y,row in enumerate(a):
            for x,tile in enumerate(row):
                # Mask
                t = tiles[tile]
                copy_tile(output_map, t[0],t[1], m, x, y)
                # Image
                if tile in result_dict:
                    t = result_dict[tile]
                    copy_tile(t[0],t[1],t[2], l, x,y)
        # Adjust selection to tiles we don't have
        # Also adjust selection in result, just
        # so users know what tiles are being generated
        pdb.gimp_selection_none(i)
        pdb.gimp_selection_none(result)
        for y,row in enumerate(a):
            for x,tile in enumerate(row):
                if tile in result_dict: continue
                if tile is EMPTY_TILE: continue
                pdb.gimp_image_select_rectangle(i,
                                                gimpenums.CHANNEL_OP_ADD,
                                                x*w,y*w,w,w)
                t = tiles[tile]
                pdb.gimp_image_select_rectangle(result,
                                                gimpenums.CHANNEL_OP_ADD,
                                                t[0]*w,t[1]*w,w,w)
        # Do the actual resynthesize call
        if True:
            pdb.plug_in_resynthesizer(i, l,
                                      int(tile_vert),
                                      int(tile_horiz),
                                      1,
                                      source.ID,
                                      source_map.ID,
                                      m.ID,
                                      map_weight,
                                      autism,
                                      neighbourhood,
                                      trys)
            # Copy to result image
            for y,row in enumerate(a):
                for x,tile in enumerate(row):
                    if tile in result_dict: continue
                    t = tiles[tile]
                    copy_tile(l, x, y, result_layer, t[0],t[1])
                    result_dict[tile] = (result_layer, t[0], t[1])
        if show:
            # For debugging
            gimp.Display(i)
            gimp.Display(mi)
        else:
            pdb.gimp_image_delete(i)
            pdb.gimp_image_delete(mi)
    synth_image([[EMPTY_TILE]],tile_vert=True,tile_horiz=True)
    synth_image([[SOLID_TILE]],tile_vert=True,tile_horiz=True)
    synth_image([[EMPTY_TILE,VERT_TILE,EMPTY_TILE]],
                tile_vert=True)
    synth_image([[EMPTY_TILE],
                 [HORIZ_TILE],
                 [EMPTY_TILE]],
                tile_horiz=True)
    synth_image([[EMPTY_TILE,EMPTY_TILE,EMPTY_TILE,EMPTY_TILE],
                 [EMPTY_TILE,TL_TILE,TR_TILE,EMPTY_TILE],
                 [EMPTY_TILE,BL_TILE,BR_TILE,EMPTY_TILE],
                 [EMPTY_TILE,EMPTY_TILE,EMPTY_TILE,EMPTY_TILE]])
    # We've now synth'd a tile representative of every possible
    # border, the rest can be done from these
    top_border = {LEFT:TL_TILE,RIGHT:TR_TILE,BOTH:VERT_TILE}
    right_border = {LEFT:TR_TILE,RIGHT:BR_TILE,BOTH:HORIZ_TILE}
    bottom_border = {LEFT:BR_TILE,RIGHT:BL_TILE,BOTH:VERT_TILE}
    left_border = {LEFT:BL_TILE,RIGHT:TL_TILE,BOTH:HORIZ_TILE}
    for border in (top_border,right_border,bottom_border,left_border):
        border[BLANK] = EMPTY_TILE
        border[SOLID] = SOLID_TILE
    for tile in tiles.keys():
        if tile in result_dict: continue
        a = [[EMPTY_TILE,EMPTY_TILE,EMPTY_TILE],
             [EMPTY_TILE,EMPTY_TILE,EMPTY_TILE],
             [EMPTY_TILE,EMPTY_TILE,EMPTY_TILE]]
        a[1][1] = tile
        a[0][1] = top_border[tile.top]
        a[1][2] = right_border[tile.right]
        a[2][1] = bottom_border[tile.bottom]
        a[1][0] = left_border[tile.left]
        # Should really do corners here too
        # but the lack of them doesn't seem
        # to be hurting the visual quality
        synth_image(a)

import gimpfu

gimpfu.register(
    "plugin_resynth_tileset_generate",
    "Generates an output map suitable for use with plugin-resynth-tileset",
    "Generates an output map suitable for use with plugin-resynth-tileset",
    "Adam Newgas",
    "Adam Newgas",
    "2013",
    "<Toolbox>/Filters/Tileset/Generate Resynth Tileset Output Map",
    "",
    [
        (gimpfu.PF_INT, "tile_width", "Tile Width", 32),
        (gimpfu.PF_INT, "inset", "Inset", 5),
        (gimpfu.PF_FLOAT, "outer_radius", "Outer Radius", 0),
        (gimpfu.PF_FLOAT, "inner_radius", "Inner Radius", 0),
        ],
    [],
    make_blob_output_pattern,
)
gimpfu.register(
    "plugin_resynth_tileset",
    "Creates a tileset using Resynthesizer",
    "Transfers a source texture from the source map to tileable texture sheet.",
    "Adam Newgas",
    "Adam Newgas",
    "2013",
    "<Toolbox>/Filters/Tileset/Resynth Tileset",
    "",
    [
        (gimpfu.PF_DRAWABLE, "source", "Source", None),
        (gimpfu.PF_DRAWABLE, "source_map", "Source Map", None),
        (gimpfu.PF_DRAWABLE, "output_map", "Output Map", None),
        (gimpfu.PF_FLOAT, "map_weight", "Weight to give map", 0.5),
        (gimpfu.PF_FLOAT, "autism", "Sensitivity", 0.12),
        (gimpfu.PF_FLOAT, "neighbourhood", "Neighbourhood Size", 30),
        (gimpfu.PF_FLOAT, "trys", "Search Thoroughness", 200),
        ],
    [],
    make_blob_output,
    )
gimpfu.main()
