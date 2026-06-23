# PDF Fetcher Utility

A command-line tool and Python library for automatically searching, retrieving, and downloading scientific research papers in PDF format. It supports direct downloading using a digital object identifier (DOI) or interactive searching and downloading via keywords/title query.

---

## 1. Features

*   **DOI-Based Downloader:** Input a DOI to clean, search, and download the paper PDF.
*   **Keyword/Title Search:** Query the Crossref API to retrieve matching papers, view titles, publication years, and authors, and interactively select which paper to download.
*   **Dual-Lookup Engine:**
    *   *First Pass:* Checks the **Unpaywall API** for legal, open-access versions of the PDF (100% compliant and fast).
    *   *Fallback Pass:* Queries working **Sci-Hub mirror services** as fallbacks to parse, extract, and download PDFs that are not legally indexed as free open-access.
*   **User-Agent Simulation:** Bypasses basic bot-blocking filters using browser-like request headers.

---

## 2. Installation & Requirements

Ensure Python 3.9+ is installed. Clone the repository or navigate to the directory:
```bash
cd E:/University/pdf-fetcher
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 3. Command-Line Usage

Run the tool using `cli.py`:

### A. Download by DOI
Specify the DOI using the `-d` or `--doi` argument:
```bash
python cli.py --doi "10.1109/CDC.2008.4739356"
```
Or specify a custom output directory or file path with `-o` or `--out`:
```bash
python cli.py --doi "10.1109/CDC.2008.4739356" --out "downloads/Moreno2008.pdf"
```

### B. Search and Download Interactively by Keywords
Specify the query string using the `-q` or `--query` argument:
```bash
python cli.py --query "Jaime Moreno Lyapunov super-twisting"
```
This prints the top 5 matches with metadata and prompts for selection:
```
[INFO] Searching for papers matching: 'Jaime Moreno Lyapunov super-twisting'...
[INFO] Searching Crossref API for keywords: 'Jaime Moreno Lyapunov super-twisting'...

--- Search Results ---
[1] A Lyapunov approach to second-order sliding mode controllers and observers
    Authors: Jaime A. Moreno, Marisol Osorio | Year: 2008
    DOI: 10.1109/cdc.2008.4739356

[2] Strict Lyapunov functions for the super-twisting algorithm
    Authors: Jaime A. Moreno | Year: 2011
    DOI: 10.1109/cdc.2011.6161250

Select a paper number to download (or 'q' to quit): 1
[INFO] Selected: 'A Lyapunov approach to second-order sliding mode controllers and observers' (DOI: 10.1109/cdc.2008.4739356)
[INFO] Querying Unpaywall API for DOI: 10.1109/cdc.2008.4739356...
...
[OK] PDF downloaded successfully to: downloads/A_Lyapunov_approach_to_second-order_sliding_mode_controllers_and_observers.pdf
[OK] Done! File saved at: E:\University\pdf-fetcher\downloads\A_Lyapunov_approach_to_second-order_sliding_mode_controllers_and_observers.pdf
```
