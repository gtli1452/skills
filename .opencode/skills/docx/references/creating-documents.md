# Creating DOCX documents

Read this file when you are generating a new `.docx` from structured content.

## Preferred toolchain
- Generate with the JavaScript `docx` package.
- Validate with `python scripts\office\validate.py output.docx`.
- Render to PDF with `python scripts\office\soffice.py --headless --convert-to pdf output.docx` when layout matters.

## Minimal skeleton
```javascript
const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
} = require("docx");

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children: [
      new Paragraph({ children: [new TextRun("Hello world")] }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => fs.writeFileSync("output.docx", buffer));
```

## Page size and margins
- `docx` defaults to A4. Set page size explicitly whenever layout matters.
- US Letter portrait: `width: 12240`, `height: 15840`
- A4 portrait: `width: 11906`, `height: 16838`
- `1440` DXA = `1` inch.

### Landscape
```javascript
const { PageOrientation } = require("docx");

page: {
  size: {
    width: 12240,
    height: 15840,
    orientation: PageOrientation.LANDSCAPE,
  },
}
```
Pass portrait dimensions and let `docx` swap them internally.

## Headings and TOC
Use the built-in heading IDs so Word can generate a table of contents.
```javascript
const { Document, Paragraph, HeadingLevel, TableOfContents } = require("docx");

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } },
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [{
    children: [
      new Paragraph({ text: "Report title", heading: HeadingLevel.HEADING_1 }),
      new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
    ],
  }],
});
```
Use `HeadingLevel` on heading paragraphs. TOCs are unreliable if you rely only on custom style names.

## Lists
Never insert literal bullet characters. Configure numbering and use it.
```javascript
const { AlignmentType, Document, LevelFormat, Paragraph, TextRun } = require("docx");

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: "numbers",
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")],
      }),
      new Paragraph({
        numbering: { reference: "numbers", level: 0 },
        children: [new TextRun("Numbered item")],
      }),
    ],
  }],
});
```

## Tables
DOCX tables render best when you set widths in three places:
- table `width`
- table `columnWidths`
- each cell `width`

Use DXA widths instead of percentages.
```javascript
const {
  BorderStyle,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  WidthType,
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };

new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4680, 4680],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 4680, type: WidthType.DXA },
          borders: { top: border, bottom: border, left: border, right: border },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun("Cell")] })],
        }),
        new TableCell({
          width: { size: 4680, type: WidthType.DXA },
          borders: { top: border, bottom: border, left: border, right: border },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph("Value")],
        }),
      ],
    }),
  ],
});
```

## Images and page breaks
```javascript
const { ImageRun, PageBreak, Paragraph } = require("docx");
const fs = require("fs");

new Paragraph({
  children: [
    new ImageRun({
      type: "png",
      data: fs.readFileSync("chart.png"),
      transformation: { width: 320, height: 180 },
      altText: { title: "Chart", description: "Quarterly chart", name: "chart.png" },
    }),
  ],
});

new Paragraph({ children: [new PageBreak()] });
```
`PageBreak` must be inside a `Paragraph`. `ImageRun` needs an explicit `type`.

## Headers and footers
```javascript
const { Document, Footer, Header, PageNumber, Paragraph, TextRun } = require("docx");

const doc = new Document({
  sections: [{
    headers: {
      default: new Header({
        children: [new Paragraph("Internal report")],
      }),
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            children: [
              new TextRun("Page "),
              new TextRun({ children: [PageNumber.CURRENT] }),
            ],
          }),
        ],
      }),
    },
    children: [],
  }],
});
```

## Validation routine
1. Generate the file.
2. Run `python scripts\office\validate.py output.docx`.
3. When layout matters, render to PDF with `python scripts\office\soffice.py --headless --convert-to pdf output.docx`.
4. Inspect the rendered PDF or page images before declaring success.

## Common failure modes
- Forgetting to set page size explicitly and getting A4 instead of Letter
- Using literal bullets or `\n` inside a paragraph instead of proper Word structures
- Using percentage table widths
- Letting `columnWidths` and cell widths disagree
- Omitting `outlineLevel` on heading styles and then wondering why the TOC is empty
- Putting `PageBreak` outside a paragraph
