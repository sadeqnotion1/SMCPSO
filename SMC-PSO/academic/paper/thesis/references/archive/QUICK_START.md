# Quick Start Guide - Thesis Sources Archive

Get started with the thesis sources archive in 5 minutes.

---

## What is This?

An organized archive of all PDF sources (books, articles, manuals) cited in your thesis, with:
- Standardized naming (BibTeX keys)
- Complete metadata (DOIs, ISBNs, URLs)
- Citation locations (where used in thesis)
- Acquisition tracking (what you have vs. need)

---

## Quick Navigation

**I want to...**

### Find a PDF by citation key
1. Open `metadata/citation_map.json`
2. Search for the BibTeX key (e.g., `Khalil2002`)
3. Note the file path (e.g., `books/Khalil2002_Nonlinear_Systems.pdf`)
4. Navigate to that folder

**Shortcut**: Use file search in your OS with the BibTeX key

### Find where a source is cited in the thesis
1. Open `metadata/thesis_locations.md`
2. Search for the BibTeX key
3. Find section numbers and page references

**Shortcut**: Search the thesis PDF for `\cite{BibtexKey}`

### See all citations in one format (IEEE, APA, BibTeX)
1. Open `metadata/full_citations.md`
2. Search for the source
3. Copy the formatted citation

### Track which PDFs I still need
1. Open `metadata/acquisition_status.md`
2. See [HAVE] vs [NEED] status
3. Follow recommended acquisition strategy

---

## Directory Structure (1-Minute Tour)

```
sources_archive/
│
├── README.md                          # Full documentation
├── QUICK_START.md                     # This file
│
├── books/                             # 7 book PDFs
│   ├── README.md
│   └── [PDF files named by BibTeX key]
│
├── articles/                          # 11 journal article PDFs
│   ├── README.md
│   └── [PDF files named by BibTeX key]
│
├── proceedings/                       # 1 conference paper PDF
│   ├── README.md
│   └── [PDF files named by BibTeX key]
│
├── manuals/                           # 2 technical manual PDFs
│   ├── README.md
│   └── [PDF files named by BibTeX key]
│
└── metadata/                          # All tracking files
    ├── citation_map.json              # BibTeX -> File path mapping
    ├── full_citations.md              # Formatted citations (IEEE/APA)
    ├── thesis_locations.md            # Where cited in thesis
    └── acquisition_status.md          # PDF download status
```

---

## Top 3 Use Cases

### 1. Download PDFs (Start Here)

**Goal**: Get all the PDF files into this archive

**Steps**:
1. Open `metadata/acquisition_status.md`
2. Follow the 4-phase acquisition strategy:
   - Phase 1: Free downloads (2-3 sources, 1-2 hours)
   - Phase 2: Institutional access (6 sources, 2-4 hours)
   - Phase 3: Purchase/request (8 sources, 3-6 hours)
   - Phase 4: Optional low-priority (4 sources, 1-2 hours)
3. As you acquire each PDF:
   - Rename to match the naming convention (see below)
   - Place in appropriate folder (books/, articles/, etc.)
   - Update `acquisition_status.md` from [NEED] to [HAVE]

**Naming Convention**:
```
Format: {BibtexKey}_{Year}_{FirstAuthor}.pdf
Example: Khalil2002_Nonlinear_Systems.pdf
```

### 2. Cite a Source Correctly

**Goal**: Get the exact citation for a reference

**Steps**:
1. Open `metadata/full_citations.md`
2. Search for the BibTeX key (e.g., `Khalil2002`)
3. Copy the citation in your preferred style:
   - IEEE (default for engineering thesis)
   - APA (if required by journal)
   - BibTeX (for LaTeX source)

**Pro Tip**: The BibTeX entries are also in `thesis/bibliography/main.bib`

### 3. Track Progress

**Goal**: See how complete the archive is

**Quick Check**:
```bash
# Count PDFs acquired
ls books/*.pdf articles/*.pdf proceedings/*.pdf manuals/*.pdf 2>nul | wc -l

# Total needed: 22 sources
```

**Detailed Status**:
- Open `metadata/acquisition_status.md`
- Check summary at top (e.g., "0/22 acquired, 0%")
- See priority distribution (HIGH/MEDIUM/LOW)

---

## Adding a New PDF (Step-by-Step)

When you download a PDF, follow these steps:

### Step 1: Rename the file
**From**: `some_random_download_name.pdf`
**To**: `{BibtexKey}_{Year}_{Title}.pdf`

**Example**:
- BibTeX key: `Khalil2002`
- Filename: `Khalil2002_Nonlinear_Systems.pdf`

### Step 2: Move to correct folder
- Books → `books/`
- Journal articles → `articles/`
- Conference papers → `proceedings/`
- Manuals → `manuals/`
- Book chapters → `articles/` (treat as articles)

### Step 3: Update metadata
Open `metadata/acquisition_status.md`:
- Change `[NEED]` to `[HAVE]`
- Update the summary count

**Example**:
```markdown
### [HAVE] Khalil2002  # Changed from [NEED]
**Status**: HAVE       # Changed from NEED
**Acquired**: 2025-12-06
```

### Step 4: Verify the file
1. Open the PDF
2. Check first page matches expected title/author
3. Verify DOI (if available) matches metadata

---

## Common Questions

### Q: What if I can't get a PDF?
**A**: Not all sources need PDFs to cite them correctly. Focus on HIGH priority sources first (see `acquisition_status.md`). You can cite without having the PDF in hand.

### Q: Can I use Sci-Hub or other questionable sources?
**A**: Use institutional access first. If unavailable, consider:
1. ResearchGate (request from authors)
2. Author preprints on personal websites
3. Interlibrary loan (ILL)
4. Purchase individual articles (~$30-40)

Avoid copyright violation - check your institution's policies.

### Q: What if the file naming is different from the convention?
**A**: The convention is flexible. Key requirement: include the BibTeX key at the start of the filename so you can find it easily.

**OK**: `Khalil2002_Nonlinear_Systems_3rd_Edition.pdf`
**OK**: `Khalil2002.pdf`
**BAD**: `Nonlinear_Systems_Khalil.pdf` (hard to search)

### Q: How do I update thesis citation locations?
**A**: Edit `metadata/thesis_locations.md`:
1. Find the source by BibTeX key
2. Fill in section/page numbers
3. Add context (why cited)

**Tip**: Use `grep -n "\\cite{Khalil2002}" thesis/**/*.tex` to find exact locations

### Q: Can I add sources not in the original bibliography?
**A**: Yes! Follow the same structure:
1. Add BibTeX entry to `thesis/bibliography/main.bib`
2. Create entry in `metadata/citation_map.json`
3. Add formatted citation to `metadata/full_citations.md`
4. Track in `metadata/acquisition_status.md`

---

## Maintenance

### Weekly Check (5 minutes)
- [ ] Count acquired PDFs vs. total (22 sources)
- [ ] Update acquisition status for any new downloads
- [ ] Verify filenames match convention

### After Major Thesis Edits
- [ ] Update `thesis_locations.md` with new citation locations
- [ ] Check if new sources were added (update all metadata)
- [ ] Re-verify which sources are actually cited (remove unused)

### Before Thesis Submission
- [ ] Verify all HIGH priority PDFs acquired
- [ ] Double-check all citations match `full_citations.md`
- [ ] Archive entire `sources_archive/` folder with thesis

---

## Next Steps

**If starting fresh** (no PDFs yet):
1. Read `metadata/acquisition_status.md` (10 min)
2. Start with Phase 1 (open access sources) (1-2 hours)
3. Move to Phase 2 (institutional access) (2-4 hours)
4. Update status as you go

**If already have some PDFs**:
1. Rename to match convention (10 min)
2. Move to appropriate folders (5 min)
3. Update `acquisition_status.md` (10 min)

**If ready to cite**:
1. Use `metadata/full_citations.md` for formatted citations
2. Use `metadata/thesis_locations.md` to verify where cited

---

## Troubleshooting

**Problem**: Can't find a PDF by filename
**Solution**: Open `metadata/citation_map.json`, search for BibTeX key

**Problem**: Don't know if a source is a book or article
**Solution**: Check `metadata/citation_map.json`, look at `"type"` field

**Problem**: Citation format doesn't match my requirements
**Solution**: Modify `metadata/full_citations.md`, or regenerate from BibTeX

**Problem**: Lost track of what I've downloaded
**Solution**: Run directory count, compare to `acquisition_status.md` summary

---

## Contact & Support

For questions about:
- **BibTeX management**: See `thesis/bibliography/main.bib`
- **Thesis structure**: See `thesis/README.md` (if exists)
- **Acquisition strategy**: See detailed guide in `metadata/acquisition_status.md`

**Last Updated**: December 6, 2025
**Version**: 1.0
