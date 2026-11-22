# Autumn ETE report QA

## Deliverables

- Editable DOCX: `output/Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.docx`
- PDF: `output/Aditya_Mazumdar_CHP400A_Autumn_ETE_Report_2026.pdf`

## Automated checks

- DOCX package: valid ZIP/OOXML; 13 embedded PNG figures.
- DOCX styles: Times New Roman, 12 pt body, 1.5 spacing, A4, mirrored margins.
- PDF: 33 A4 pages (`595.28 x 841.89 pt`), below 50-page autumn limit.
- Required sections: certificate, declarations, acknowledgements, abstract, contents, lists, nomenclature, five chapters, data availability, AI disclosure, references, and appendices.
- Required numerical findings: `19.75%`, `10.43%`, `6.91%`, `<0.24%`, `0.90572`, and `49.65%`.
- Report suite: 14/14 tests passed; capillary-wave project suite: 19/19 tests passed.
- No missing-glyph question marks, `TODO`, `TBD`, `FIXME`, unsupported novelty phrase, or table-of-contents update message.
- Data archive URL appears in both declaration and Data Availability section; no pending marker remains.
- Main `a0 = 0.5`, `N = 128` archive contains 500 Fourier samples through `tau = 24.95` and six profile frames. Recomputed normalized peaks are `0.1975028527`, `0.1043069402`, and `0.0690659471` for modes 3, 5, and 7.

## Visual inspection

Rendered and inspected PDF pages:

- Page 1: cover and identity details.
- Page 3: declarations and signature spaces.
- Page 4: supervisor-comments space.
- Page 9: corrected four-item list of tables.
- Pages 15-16: governing equations, separate grid/boundary descriptions, and bordered parameter table.
- Page 20: gravity-wave figures and results table.
- Page 25: Fourier grid sensitivity and travelling-wave discussion.
- Page 30: ACS-style references.
- Pages 31-33: complete reproduction commands and bordered project-file inventory.

No clipping, overlap, blank figure, or unreadable caption found on inspected pages. Page 4 intentionally leaves room for handwritten supervisor comments.

## Reproducibility

```bash
python3 btp-autumn-ete-report/build_report.py
python3 btp-autumn-ete-report/render_pdf.py
python3 -m unittest discover -s btp-autumn-ete-report -p 'test_*.py' -v
```

## Required before submission

1. Confirm supervisor name/title and obtain signatures.
2. Run Turnitin and obtain supervisor verification.
3. Let supervisor review scientific wording and approve final version.
4. Open editable DOCX in Microsoft Word on a machine with Times New Roman installed and update it if department requires exact Word pagination.

## Known limits

- Local machine lacks LibreOffice Writer and Microsoft Times New Roman. DOCX explicitly requests Times New Roman; locally generated PDF uses PostScript Times Roman, its closest built-in equivalent.
- PDF was rendered from DOCX OOXML with a local deterministic renderer. Its pagination may differ slightly when DOCX opens in Microsoft Word.
- DOCX retains mathematical symbols. PDF equations are typeset as high-resolution equation images so integrals, fractions, Greek letters, subscripts, superscripts, and radicals render correctly despite limited PostScript Unicode support.
- Travelling-wave result remains one small-amplitude, pure-capillary case. Gravity, unequal fluid properties, and nonlinear travelling-wave interactions remain future work.
