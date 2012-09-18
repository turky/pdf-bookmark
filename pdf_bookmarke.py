#!/usr/bin/env python3
# fileencoding: utf-8
# pdf-bookmarker.py: Add bookmark to PDF from tabluar text.
# Akihiro Takizawa<akihiro.takizawa@gmail.com>

import argparse
import logging
from tempfile import mktemp
from unicodedata import normalize

# convert roman number strng to integer
def roman_to_int(roman_num):
    roman_vals = {"i":1, "v":5, "x":10, "l":50, "c":100, "d":500, "m":1000}
    int_val = 0
    last_val = 0
    for temp_item in iter(roman_num.lower()[::-1]):
        try:
            temp_val = roman_vals[temp_item]
            if temp_val >= last_val:
                int_val = int_val + temp_val
            else:
                int_val = int_val - temp_val
            last_val = temp_val
        except StopIteration:
            break
    return int_val

# this method work correct with Python3.
def conv_to_oct(source):
    buf = ""
    for c in source:
        buf = buf + oct(c.encode("utf-16be")[0]).replace("0o", "\\") \
            + oct(c.encode("utf-16be")[1]).replace("0o", "\\")
    return "\\376\\377" + buf

#build single mark
def build_mark(title, page, child_num=0, hidden=True):
    if page != "":
        base_mark = "/Title (" + conv_to_oct(title) + \
            ") /Page %d /OUT pdfmark\n" %(page)
        if child_num == 0:
            return "[" + base_mark
        else:
            if hidden:
                return "[/Count -%d " % (child_num) + base_mark
            else:
                return "[/Count %d " % (child_num) + base_mark
    else:
        return page

def save_bookmark(fname, data):
    fp = open(fname,"w")
    fp.write(data)
    fp.close()

# simgle line to mark elements, with detect toc depth
def line_to_elements(line):
    text, page = line.split("\t")
    depth = 0
    if text.startswith(" "):
        for item in text.split("    "):
            if item == "":
                depth = depth + 1
            else:
                text = item.strip()
    return (depth, text, page)

def build_bookmark(tocfile, forwardpages, hidelevel=1):
    with open(tocfile, "r", encoding="utf-8") as source:
        marklist = []
        last_depth = 0
        child_num = 0
        childrens = {"l0":0}
        # read TOC file from end.
        for line in reversed(source.readlines()):
            try:
                depth, title, page = line_to_elements(line.rstrip())
                if page.isdigit():
                    page = int(page)+forwardpages
                elif page.isalpha():
                    page = roman_to_int(page) + 1
                else:
                    page = ""
                
                if depth > last_depth:
                    #init next level counter
                    try:
                        if childrens["l"+str(depth)] == 0:
                            childrens["l"+str(depth)] = 1
                    except KeyError:
                        childrens["l"+str(depth)] = 1
                elif depth == last_depth:
                    #count up current level
                    childrens["l"+str(depth)] += 1
                elif depth < last_depth:
                    #return next level counter
                    cur_depth = str(last_depth)
                    child_num = childrens["l"+cur_depth]
                    childrens["l"+cur_depth] = 0
                    childrens["l"+str(depth)] += 1
                mark = build_mark(title, page, child_num, depth<=hidelevel)
                marklist.append(mark)
                child_num = 0
                last_depth = depth
            except ValueError:
                pass
            except:
                raise
    marklist.reverse() # reverse bookmark to page order
    return "".join(marklist)
  
def main(tocfile, inputpdf=None, outputpdf=None, 
        hidelevel=1, forwardpages=0):
    from subprocess import call
    
    bookmark = build_bookmark(tocfile, forwardpages, hidelevel)
    if inputpdf == None and outputpdf==None:
        from sys import stdout
        stdout.write(bookmark)
    else:
        #process outputpdf and write it to <outputpdf>.
        temptoc = mktemp()
        fp = open(temptoc,"w")
        fp.write(bookmark)
        fp.close()
        cmd = "gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=%(outputpdf)s %(inputpdf)s %(temptoc)s" % vars()
        return call(cmd.split())
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser( \
        description="Add bookmark to PDF from teb separated TOC text.")
    parser.add_argument("toc", help="Teb separated TOC file.")
    parser.add_argument("-i", "--inputpdf", help="input PDF.")
    parser.add_argument("-o", "--outputpdf", help="output PDF with bookmark.")
    parser.add_argument("-l", "--hidelevel", type=int, \
        default=1, help="hidden bookmark level.")
    parser.add_argument("-f", "--forwardpages", type=int, \
        help="forward page offset.")
    options = parser.parse_args()
    if options.toc == None:
        parser.print_help()
    else:
        main(options.toc, options.inputpdf, options.outputpdf, \
            options.hidelevel, options.forwardpages)

