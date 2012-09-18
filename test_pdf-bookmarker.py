#!/usr/bin/env python
# fileencoding: utf-8
import pytest
from os.path import abspath, dirname, join
from pdf_bookmarke import build_bookmark, build_mark, conv_to_oct, \
    roman_to_int, line_to_elements

def test_conv_to_oct():
    assert(conv_to_oct("1章 理解しやすいコード") == '\\376\\377\\0\\61\\172\\340\\0\\40\\164\\6\\211\\343\\60\\127\\60\\204\\60\\131\\60\\104\\60\\263\\60\\374\\60\\311')

def test_build_mark():
    title, page = "1章 理解しやすいコード	1".split("\t")
    assert(build_mark(title, int(page), 0) == "[/Title (\\376\\377\\0\\61\\172\\340\\0\\40\\164\\6\\211\\343\\60\\127\\60\\204\\60\\131\\60\\104\\60\\263\\60\\374\\60\\311) /Page 1 /OUT pdfmark\n")
    
def test_roman_to_int():
    assert(roman_to_int("vi") == 6)
    assert(roman_to_int("MDCCCCX") == 1910)
    assert(roman_to_int("MDCCCCLXXXXVIIII") == 1999)
    assert(roman_to_int("MCMXCIX") == 1999)
    assert(roman_to_int("MIM") == 1999)

def test_line_to_elements():
    assert(line_to_elements("1章 理解しやすいコード	1") == (0, "1章 理解しやすいコード", "1"))
    assert(line_to_elements("    1章 理解しやすいコード	1") == (1, "1章 理解しやすいコード", "1"))
    assert(line_to_elements("        1章 理解しやすいコード	1") == (2, "1章 理解しやすいコード", "1"))
    assert(line_to_elements("            1章 理解しやすいコード	1") == (3, "1章 理解しやすいコード", "1"))
    assert(line_to_elements("                1章 理解しやすいコード	1") == (4, "1章 理解しやすいコード", "1"))

def test_build_bookmark():
    current_path = abspath(dirname(__file__))
    assert(build_bookmark(join(current_path, "./fixture/source.txt"), 0) \
        == open(join(current_path, "./fixture/distinate.txt")).read())
