# Editing presentations

## Template-based workflow
When using an existing presentation as a template:

1. **Analyze existing slides**:
   ```bash
   python scripts\thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```
   Review `thumbnails.jpg` to understand layouts, then inspect the extracted text to find placeholders and speaker-note content.

2. **Plan slide mapping**:
   - Match each content section to a template slide before editing XML
   - Use varied layouts; avoid turning every slide into the same title-plus-bullets pattern
   - Remove unused visual groups instead of leaving empty placeholders behind

3. **Unpack**:
   ```bash
   python scripts\office\unpack.py template.pptx unpacked
   ```

4. **Complete structural changes before text edits**:
   - Delete unwanted slides by removing their `<p:sldId>` entries from `ppt\presentation.xml`
   - Duplicate or add slides with `python scripts\add_slide.py unpacked slide2.xml`
   - Reorder slides inside `<p:sldIdLst>`

5. **Edit slide content**:
   - Update the individual `slideN.xml` files under `unpacked\ppt\slides\`
   - Replace all placeholder text, images, icons, charts, captions, and citations
   - Keep each logical list item or step in its own `<a:p>` paragraph instead of concatenating everything into one run

6. **Clean**:
   ```bash
   python scripts\clean.py unpacked
   ```

7. **Pack**:
   ```bash
   python scripts\office\pack.py unpacked output.pptx --original template.pptx
   ```

8. **QA**:
   ```bash
   python -m markitdown output.pptx
   python -m markitdown output.pptx | rg -i "xxxx|lorem|ipsum|this.*(page|slide).*layout"
   ```
   Then render to PDF or images for a visual review.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts\office\unpack.py` | Extract and pretty-print PPTX XML |
| `scripts\add_slide.py` | Duplicate a slide or create one from a layout |
| `scripts\clean.py` | Remove orphaned slides, rels, and media |
| `scripts\office\pack.py` | Repack and validate the edited deck |
| `scripts\thumbnail.py` | Create a slide thumbnail grid for template analysis |

## Slide operations
Slide order lives in `ppt\presentation.xml` inside `<p:sldIdLst>`.

- **Reorder**: rearrange the `<p:sldId>` elements
- **Delete**: remove the `<p:sldId>` entry, then run `clean.py`
- **Add**: use `add_slide.py`; do not manually copy slide files because the script updates relationships and content types for you

## Editing content safely
- Edit the slide XML precisely; do not do broad search-and-replace across the whole deck unless you have inspected the effect
- Preserve existing formatting runs and paragraph properties when possible
- Bold slide titles, section headers, and inline labels with `b="1"` on `<a:rPr>`
- Never use literal Unicode bullet characters; use the slide's existing list structures such as `<a:buChar>` or `<a:buAutoNum>`
- Copy the original `<a:pPr>` when splitting or expanding content so line spacing and indentation stay consistent

### Multi-item content
If the source has multiple steps or bullet items, create separate `<a:p>` elements for each one.

**Wrong:** one paragraph containing every step as a long sentence.

**Right:** one paragraph per step or bullet, reusing the template's paragraph settings.

## Smart quotes and whitespace
The unpack and pack helpers preserve smart quotes, but when you add new text directly in XML, use entities such as `&#x201C;` and `&#x201D;` for quote marks.

Add `xml:space="preserve"` to text nodes that need leading or trailing spaces.

## Visual QA
Render the deck after every substantial round of edits.

```bash
python scripts\office\soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

Check the rendered slides for:
- overlapping shapes or text
- cut-off text and narrow text boxes
- leftover placeholders or empty template cards
- uneven spacing or poor alignment
- low contrast between text and the background
- objects sitting too close to the slide edge

## Common pitfalls
- Clearing text but forgetting to remove the matching image, icon, or shape
- Stretching a template beyond its capacity instead of deleting unused elements
- Letting long replacement text wrap into design elements
- Forgetting to run `clean.py` after deleting or duplicating slides
