# Build the manuscript

The released `main.tex` contains the accepted final R3 scientific report with the v1.0.1 author metadata correction. The ten-entry `references.bib`, all input tables and four vector figures retain their accepted scientific content. The already-exported compiled report is `../critical-miss-evaluation.pdf`. Version 1.0.1 adds Xiaotong Wu's name, affiliation and email, together with “Research Advisor: Dr. Zhiyu Quan”; the advisor is not listed as a coauthor. The scientific text and numbers are unchanged.

Install a TeX distribution with IEEEtran, mathptmx, amsmath/amssymb, booktabs, graphicx, url, balance and hyperref. IEEEtran.cls/IEEEtran.bst are normal distribution dependencies, not vendored third-party files.

From this directory:

```bash
latexmk -pdf main.tex
```

Or run pdflatex, bibtex, and two further pdflatex passes. A normal Tectonic build with BibTeX support is another option. Runtime binaries are not included. Compilation has no scientific side effects and does not invoke the analysis scripts. Exact exported PDF bytes may differ by toolchain/metadata; the supplied PDF hash is in the [public release manifest](../../provenance/PUBLIC_RELEASE_MANIFEST.json).
