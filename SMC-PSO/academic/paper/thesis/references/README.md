# Thesis Sources Archive

This directory contains all PDF sources referenced in the thesis with their exact citation addresses.

## Directory Structure

```
sources_archive/
├── books/              # Book references (7 sources)
├── articles/           # Journal articles (11 sources)
├── proceedings/        # Conference proceedings (1 source)
├── manuals/            # Technical manuals (2 sources)
├── metadata/           # Metadata and citation mappings
│   ├── citation_map.json          # JSON mapping of BibTeX keys to file paths
│   ├── full_citations.md          # Complete formatted citations
│   └── thesis_locations.md        # Where each source is cited in thesis
└── README.md           # This file
```

## File Naming Convention

All PDFs are named using their BibTeX citation keys for easy cross-referencing:

- **Format**: `{BibtexKey}_{Year}_{FirstAuthor}.pdf`
- **Example**: `Khalil2002_Nonlinear_Systems.pdf` (BibTeX key: `Khalil2002`)

## Quick Reference

### Books (7)
- Khalil2002 - Nonlinear Systems (3rd ed.)
- Shtessel2014 - Sliding Mode Control and Observation
- BoubakersIriarte2017 - The Inverted Pendulum in Control Theory and Robotics
- AstromHagglund2006 - Advanced PID Control
- EdwardsSpurgeon1998 - Sliding Mode Control: Theory and Applications
- FantoniLozano2002 - Non-linear Control for Underactuated Mechanical Systems
- ODwyer2009 - Handbook of PI and PID Controller Tuning Rules (3rd ed.)

### Journal Articles (11)
- Utkin1977 - Variable structure systems with sliding modes
- Levant2007 - Principles of 2-sliding mode design
- SlotineSastry1983 - Tracking control of non-linear systems using sliding surfaces
- SlotineCoetsee1986 - Adaptive sliding controller synthesis for non-linear systems
- Plestan2010 - New methodologies for adaptive sliding mode control
- ClercKennedy2002 - The particle swarm - explosion, stability, and convergence
- Zhou2012 - Robust adaptive output control of uncertain nonlinear plants
- Khanesar2013 - Sliding mode control of rotary inverted pendulum
- Dash2015 - Adaptive fractional integral terminal sliding mode power control
- Collins2005 - Efficient bipedal robots based on passive-dynamic walkers
- Deb2002 - A fast and elitist multiobjective genetic algorithm: NSGA-II

### Conference Proceedings (1)
- Kennedy1995 - Particle swarm optimization (IEEE ICNN)

### Technical Manuals (2)
- Quanser2020 - Linear Inverted Pendulum Experiment User Manual
- ECP2020 - Model 505 Inverted Pendulum System User Manual

### Book Chapters (1)
- Spong1998 - Underactuated mechanical systems (in "Control Problems in Robotics")

## Usage

### Finding a Source by Citation Key

1. Check `metadata/citation_map.json` for the file path
2. Navigate to the appropriate subdirectory
3. Open the PDF using the standardized filename

### Finding Where a Source is Cited

1. Check `metadata/thesis_locations.md` for section/page references
2. Search the thesis PDF using the BibTeX key (e.g., `\cite{Khalil2002}`)

### Adding New Sources

1. Download the PDF from the publisher/repository
2. Rename using the convention: `{BibtexKey}_{Year}_{FirstAuthor}.pdf`
3. Place in the appropriate subdirectory
4. Update `metadata/citation_map.json`
5. Add full citation to `metadata/full_citations.md`
6. Record thesis location in `metadata/thesis_locations.md`

## Metadata Files

### citation_map.json
JSON mapping of BibTeX keys to file paths with metadata:
```json
{
  "Khalil2002": {
    "file": "books/Khalil2002_Nonlinear_Systems.pdf",
    "type": "book",
    "year": 2002,
    "title": "Nonlinear Systems",
    "authors": ["Khalil, Hassan K."],
    "doi": null,
    "url": null
  }
}
```

### full_citations.md
Complete formatted citations in multiple styles (IEEE, APA, BibTeX)

### thesis_locations.md
Cross-reference showing where each source is cited in the thesis:
- Section numbers
- Page numbers
- Context of citation (background, methodology, results, etc.)

## Acquisition Status

**Legend**:
- [HAVE] PDF available in archive
- [NEED] PDF not yet acquired
- [OPEN] Open access available online
- [PAYWALL] Requires institutional access

See `metadata/acquisition_status.md` for detailed status of each source.

## License and Usage

All PDFs in this archive are for **personal research and educational use only**.
Respect copyright and publisher policies. Do not redistribute without permission.

**Last Updated**: December 6, 2025
**Thesis Version**: v2.1
**Total Sources**: 27 (21 unique)
