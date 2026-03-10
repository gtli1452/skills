# Editing existing DOCX files

Read this file when you must preserve an existing Word document's structure, style, or template while making file-first edits.

## Inspect before changing
- Convert legacy `.doc` first:
  `python scripts\office\soffice.py --headless --convert-to docx input.doc`
- Extract text quickly:
  `pandoc --track-changes=all input.docx -o output.md`
- Unpack for raw XML:
  `python scripts\office\unpack.py input.docx unpacked`

## Standard edit loop
1. Unpack the document:
   `python scripts\office\unpack.py input.docx unpacked`
2. Edit files under `unpacked\word\`
3. Repack against the original:
   `python scripts\office\pack.py unpacked output.docx --original input.docx`
4. Validate or render:
   - `python scripts\office\validate.py output.docx`
   - `python scripts\office\soffice.py --headless --convert-to pdf output.docx`

## Editing rules
- Make the smallest XML change that solves the task.
- Preserve existing `<w:rPr>` and paragraph properties whenever possible.
- Use smart quote entities for new text:
  - `&#x2018;` left single
  - `&#x2019;` apostrophe or right single
  - `&#x201C;` left double
  - `&#x201D;` right double
- Add `xml:space="preserve"` when a text node needs leading or trailing spaces.

## Tracked changes
Use `Editor` as the default author unless the user asks for a specific name.

### Insertion
```xml
<w:ins w:id="1" w:author="Editor" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

### Deletion
```xml
<w:del w:id="2" w:author="Editor" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

### Minimal edits
Change only the portion that changes, not the whole sentence or paragraph.
```xml
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Editor" w:date="...">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Editor" w:date="...">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

### Deleting a full paragraph or list item
When removing all content from a paragraph, also mark the paragraph mark as deleted or Word may leave an empty paragraph behind.
```xml
<w:p>
  <w:pPr>
    <w:numPr>...</w:numPr>
    <w:rPr>
      <w:del w:id="1" w:author="Editor" w:date="2025-01-01T00:00:00Z"/>
    </w:rPr>
  </w:pPr>
  <w:del w:id="2" w:author="Editor" w:date="2025-01-01T00:00:00Z">
    <w:r><w:delText>Entire paragraph content...</w:delText></w:r>
  </w:del>
</w:p>
```

## Comments
Use `scripts\comment.py` for comment boilerplate instead of hand-editing every related XML file.
```bash
python scripts\comment.py unpacked 0 "Comment text with &amp; and &#x2019;" --author "Editor"
python scripts\comment.py unpacked 1 "Reply text" --parent 0 --author "Editor"
```
After running the script, add the markers to `document.xml`.

Comment range markers must be direct children of `<w:p>`, never nested inside `<w:r>`.
```xml
<w:commentRangeStart w:id="0"/>
<w:r><w:t>reviewed text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r>
  <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
  <w:commentReference w:id="0"/>
</w:r>
```

## XML safety rules
- Element order in `<w:pPr>` matters: `<w:pStyle>`, `<w:numPr>`, `<w:spacing>`, `<w:ind>`, `<w:jc>`, then `<w:rPr>`
- Use `<w:delText>` inside `<w:del>` instead of `<w:t>`
- Replace whole runs when adding tracked changes; do not inject change tags inside an existing run
- Keep RSIDs as 8-digit hex values when editing them manually
- Preserve relationships and content types if you add images or other parts

## Accepting changes
To ship a clean document with changes accepted:
```bash
python scripts\accept_changes.py input.docx output.docx
```

## Visual QA
When layout matters:
1. Convert to PDF with `python scripts\office\soffice.py --headless --convert-to pdf output.docx`
2. Optionally convert the PDF to images for page-by-page review
3. Check for unexpected page breaks, empty list items after deletions, broken tables, misplaced comment markers, and text that lost formatting

## Common failure modes
- Editing the wrong XML part and missing headers, footers, or footnotes
- Replacing too much text and destroying run-level formatting
- Forgetting `xml:space="preserve"` around leading or trailing spaces
- Putting comment markers inside runs
- Using straight quotes where the surrounding document uses smart quotes
