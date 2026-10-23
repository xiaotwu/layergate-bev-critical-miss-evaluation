# Build the manuscript

The released `main.tex`, ten-entry `references.bib`, all input tables and four vector figures are copied from the accepted final R3 project. The already-exported document is `../critical-miss-evaluation.pdf` (eleven pages). The original scientific text and numbers are not changed for publication.

Install a TeX distribution with IEEEtran, mathptmx, amsmath/amssymb, booktabs, graphicx, url, balance and hyperref. IEEEtran.cls/IEEEtran.bst are normal distribution dependencies, not vendored third-party files.

From this directory:

```bash
latexmk -pdf main.tex
```

Or run pdflatex, bibtex, and two further pdflatex passes. A normal Tectonic build with BibTeX support is another option. Runtime binaries are not included. Compilation has no scientific side effects and does not invoke the analysis scripts. Exact exported PDF bytes may differ by toolchain/metadata; the supplied PDF hash is in `provenance/PUBLIC_RELEASE_MANIFEST.json`.
