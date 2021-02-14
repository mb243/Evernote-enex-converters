#!/usr/bin/env python3

import base64
import html2markdown
import html2text
import xml.etree.ElementTree
import markdownify

enex_filename = ''  # Full path to enex file to convert

def read_enex_file(filename: str) -> str:
  with open(filename, 'rb') as file:
    contents = file.read()
  return contents

def parse_note_content(note_content: str) -> str:
  # Strip the XML headers off the note content
  note_content = note_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
  note_content = note_content.replace('<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">', '')
  note_content = markdownify.markdownify(note_content)
  return note_content

def parse_xml(filename: str) -> str:
  tree = xml.etree.ElementTree.parse(filename)
  root = tree.getroot()
  for note in root.findall('note'):
    print('note: ', note.tag)  # should be child.tag = 'note'
    print('title: ', note.find('title').text)
    createddate = note.find('created').text
    for resource in note.findall('resource'):
      mimetype = resource.find('mime').text
      encoding = resource.find('data').attrib['encoding']
      data = resource.find('data').text
      outfile = resource.find('resource-attributes').find('file-name').text  # prefer the stored filename
      if not outfile:  # or generate a new one if there's not one defined
        outfile = f"{createddate}-{abs(hash(data))}.{mimetype.split('/')[1]}"
      if encoding == 'base64':
        with open(outfile, 'wb') as file:
          file.write(base64.b64decode(data))


def main():
    filename = enex_filename
    parse_xml(filename)


if __name__ == "__main__":
  main()
