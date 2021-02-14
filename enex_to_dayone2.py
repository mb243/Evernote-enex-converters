#!/usr/bin/env python3

import base64
import html2markdown
import html2text
import xml.etree.ElementTree
import markdownify
import subprocess

journal_name = 'Test'  # Jornal to add exported entries to
journal_file = ''  # Full path to enex file containing entries

def read_enex_file(filename: str) -> str:
  with open(filename, 'rb') as file:
    contents = file.read()
  return contents

def parse_note_content(note_content: str) -> str:
  # Strip the XML headers off the note content
  note_content = note_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
  note_content = note_content.replace('<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">', '')

  # note_content = html2text.html2text(note_content)
  # note_content = html2markdown.convert(note_content)
  note_content = markdownify.markdownify(note_content)
  return note_content

def parse_xml(filename: str) -> str:
  tree = xml.etree.ElementTree.parse(filename)
  root = tree.getroot()
  for note in root.findall('note'):
    resources = []
    print('note: ', note.tag)  # should be child.tag = 'note'
    print('title: ', note.find('title').text)
    createddate = note.find('created').text
    print('created date: ', createddate)  # 20190412T234306Z
    note_content = "# " + note.find('title').text
    note_content = note_content + '\n' + parse_note_content(note.find('content').text)
    for resource in note.findall('resource'):
      mimetype = resource.find('mime').text
      encoding = resource.find('data').attrib['encoding']
      data = resource.find('data').text
      outfile = resource.find('resource-attributes').find('file-name').text  # prefer the stored filename
      if not outfile:  # or generate a new one if there's not one defined
        outfile = f"{createddate}-{abs(hash(data))}.{mimetype.split('/')[1]}"
      # print(outfile)
      resources.append(outfile)
      
      if encoding == 'base64':
        with open(outfile, 'wb') as file:
          file.write(base64.b64decode(data))
    command = ['dayone2', '-j', journal_name, '-d', createddate]
    if resources:
      command.append('-p')
      command = command + resources
      command.append('--')
    command = command + ['new', note_content]
    print(command)
    subprocess.check_output(command)
    

def main():
    filename = journal_file
    parse_xml(filename)

if __name__ == "__main__":
  main()
