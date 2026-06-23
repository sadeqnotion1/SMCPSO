#======================================================================================\\\
#============================ fetcher.py ==============================================\\\
#======================================================================================\\\

import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

class PDFFetcher:
    """
    Core engine for searching and downloading scientific paper PDFs using DOIs or keywords.
    """

    def __init__(self):
        # List of working Sci-Hub mirrors to try as fallbacks
        self.sci_hub_mirrors = [
            "https://sci-hub.se",
            "https://sci-hub.ru",
            "https://sci-hub.st",
            "https://sci-hub.shop"
        ]
        # Standard browser headers to avoid automated script blocks
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        self.reset()

    def reset(self) -> None:
        """Reset internal state, clearing tracked forbidden or blocked URLs."""
        self.forbidden_urls = []


    def clean_doi(self, doi: str) -> str:
        """Clean and extract the DOI from a string or URL."""
        doi = doi.strip()
        # Regex to match standard DOI format (starts with 10.)
        match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', doi, re.IGNORECASE)
        if match:
            return match.group(1)
        return doi

    def fetch_from_unpaywall(self, doi: str) -> str:
        """
        Attempt to retrieve a legal open-access PDF link via the Unpaywall API.
        """
        cleaned_doi = self.clean_doi(doi)
        # Unpaywall requires an email parameter to prevent abuse
        url = f"https://api.unpaywall.org/v2/{cleaned_doi}?email=openaccess_fetcher@example.com"
        
        try:
            print(f"[INFO] Querying Unpaywall API for DOI: {cleaned_doi}...")
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_oa") and data.get("best_oa_location"):
                    pdf_url = data["best_oa_location"].get("url_for_pdf")
                    if pdf_url:
                        print(f"[OK] Found legal open-access PDF URL via Unpaywall: {pdf_url}")
                        return pdf_url
            elif response.status_code == 403:
                self.forbidden_urls.append((url, f"HTTP {response.status_code} Forbidden"))
            print("[INFO] No legal open-access PDF location found via Unpaywall.")
        except Exception as e:
            print(f"[WARNING] Unpaywall API query failed: {str(e)}")
            self.forbidden_urls.append((url, f"Exception: {str(e)}"))
        return ""

    def fetch_from_scihub(self, doi: str) -> str:
        """
        Attempt to retrieve the PDF from Sci-Hub mirrors.
        """
        cleaned_doi = self.clean_doi(doi)
        
        for mirror in self.sci_hub_mirrors:
            mirror_url = f"{mirror}/{cleaned_doi}"
            try:
                print(f"[INFO] Querying Sci-Hub mirror: {mirror} for DOI: {cleaned_doi}...")
                response = requests.get(mirror_url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"[WARNING] Mirror {mirror} returned status code {response.status_code}")
                    if response.status_code == 403:
                        self.forbidden_urls.append((mirror_url, f"HTTP {response.status_code} Forbidden"))
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Check for meta tag citation_pdf_url first
                meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
                pdf_url = ""
                
                if meta_pdf and meta_pdf.get("content"):
                    pdf_url = meta_pdf["content"]
                else:
                    # Check for iframe or embed elements commonly used by Sci-Hub to show PDFs
                    pdf_elem = soup.find("iframe", id="pdf") or soup.find("embed", id="pdf")
                    if pdf_elem and pdf_elem.get("src"):
                        pdf_url = pdf_elem["src"]
                    else:
                        # Look for links or buttons that point directly to the PDF
                        download_btn = soup.find("button", onclick=True)
                        if download_btn:
                            match = re.search(r"location.href\s*=\s*['\"]([^'\"]+)['\"]", download_btn["onclick"])
                            if match:
                                pdf_url = match.group(1)
                
                if pdf_url:
                    # Format relative/protocol-relative URLs
                    if pdf_url.startswith("//"):
                        pdf_url = "https:" + pdf_url
                    elif pdf_url.startswith("/"):
                        parsed_mirror = urllib.parse.urlparse(mirror)
                        pdf_url = f"{parsed_mirror.scheme}://{parsed_mirror.netloc}{pdf_url}"
                    
                    print(f"[OK] Found PDF URL on Sci-Hub mirror: {pdf_url}")
                    return pdf_url
                
            except Exception as e:
                print(f"[WARNING] Query failed for mirror {mirror}: {str(e)}")
                
        print("[ERROR] Failed to locate PDF on all Sci-Hub mirrors.")
        return ""

    def download_pdf(self, pdf_url: str, dest_path: str) -> bool:
        """
        Download the PDF from the given URL and save it to the destination path.
        """
        try:
            print(f"[INFO] Downloading PDF from: {pdf_url}...")
            response = requests.get(pdf_url, headers=self.headers, stream=True, timeout=30)
            if response.status_code == 200:
                # Ensure the destination folder exists
                os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
                
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Basic sanity check to ensure we didn't just download an HTML error page
                if os.path.getsize(dest_path) > 2000:
                    with open(dest_path, "rb") as test_f:
                        start_bytes = test_f.read(4)
                        if start_bytes == b"%PDF":
                            print(f"[OK] PDF downloaded successfully to: {dest_path}")
                            # Clean up old failure report txt if it exists
                            txt_path = os.path.splitext(dest_path)[0] + ".txt"
                            if os.path.exists(txt_path):
                                try:
                                    os.remove(txt_path)
                                except Exception:
                                    pass
                            return True
                    print("[ERROR] Downloaded file is not a valid PDF document (header mismatch).")
                    self.forbidden_urls.append((pdf_url, "Downloaded file header is not %PDF"))
                else:
                    print("[ERROR] Downloaded file is too small to be a valid PDF.")
                    self.forbidden_urls.append((pdf_url, f"Downloaded file size ({os.path.getsize(dest_path)} bytes) is too small for PDF"))
                
                # Cleanup if the download was invalid
                if os.path.exists(dest_path):
                    os.remove(dest_path)
            else:
                print(f"[ERROR] Download failed with HTTP status code: {response.status_code}")
                self.forbidden_urls.append((response.url, f"HTTP {response.status_code} Error"))
        except Exception as e:
            print(f"[ERROR] Failed to download PDF: {str(e)}")
            self.forbidden_urls.append((pdf_url, f"Exception: {str(e)}"))
        return False

    def search_crossref(self, query: str, limit: int = 5) -> list:
        """
        Query Crossref API to search for research papers by keyword or direct DOI lookup.
        """
        cleaned_query = query.strip()
        # Detect if the query is a direct DOI
        is_direct_doi = False
        cleaned_doi = self.clean_doi(cleaned_query)
        if "/" in cleaned_doi and (cleaned_doi.startswith("10.") or re.match(r"^10\.\d{4,}", cleaned_doi)):
            url = f"https://api.crossref.org/works/{urllib.parse.quote(cleaned_doi)}"
            is_direct_doi = True
            print(f"[INFO] Direct Crossref API lookup for DOI: '{cleaned_doi}'...")
        else:
            encoded_query = urllib.parse.quote(cleaned_query)
            url = f"https://api.crossref.org/works?query={encoded_query}&rows={limit}"
            print(f"[INFO] Searching Crossref API for keywords: '{cleaned_query}'...")
        
        results = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if is_direct_doi:
                    items = [data.get("message", {})]
                else:
                    items = data.get("message", {}).get("items", [])
                
                for item in items:
                    doi = item.get("DOI")
                    title = " ".join(item.get("title", ["Unknown Title"]))
                    # Gather authors
                    authors_list = item.get("author", [])
                    authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list[:3]])
                    if len(authors_list) > 3:
                        authors += " et al."
                    # Gather publication year
                    pub_date = item.get("published-print") or item.get("published-online") or item.get("created")
                    year = pub_date.get("date-parts", [[0]])[0][0] if pub_date else "Unknown Year"
                    
                    results.append({
                        "doi": doi,
                        "title": title,
                        "authors": authors if authors else "Unknown Authors",
                        "year": year
                    })
            else:
                print(f"[ERROR] Crossref query failed with HTTP status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Crossref query failed: {str(e)}")
            
        return results

    def verify_match(self, query: str, title: str, paper_year: str = "") -> bool:
        """
        Verify if the matched title and year are a reasonable match for the query.
        """
        q_low = query.lower()
        t_low = title.lower()
        
        # 1. Double pendulum check
        if "double" in q_low and "double" not in t_low:
            return False
            
        # 2. Year check
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', query)
        if year_match and paper_year and paper_year != "Unknown Year":
            try:
                query_year = int(year_match.group(1))
                if abs(int(paper_year) - query_year) > 1:
                    return False
            except ValueError:
                pass
                
        # 3. Overlap check
        q_words = set(re.findall(r'\b\w{4,}\b', q_low))
        exclude = {'prasad', 'tyagi', 'gupta', 'oklahoma', 'university', 'state', 'thesis', 'systems', 'system'}
        q_words = q_words - exclude
        
        t_words = set(re.findall(r'\b\w{4,}\b', t_low))
        if q_words:
            overlap = q_words.intersection(t_words)
            ratio = len(overlap) / len(q_words)
            if ratio < 0.8: # At least 80% overlap of key words to prevent mismatches
                return False
                
        return True



    def save_failure_info(self, dest_path: str, doi: str, pdf_url: str, reason: str, metadata: dict = None) -> str:
        """
        Write a text file containing the metadata, landing page DOI URL, attempted PDF URL, 
        and download failure reason in the destination directory.
        """
        # Form the text file path by changing the extension to .txt
        base_path, _ = os.path.splitext(dest_path)
        txt_path = base_path + ".txt"
        
        # Pull metadata values
        title = metadata.get("title", "Unknown Title") if metadata else "Unknown Title"
        authors = metadata.get("authors", "Unknown Authors") if metadata else "Unknown Authors"
        year = metadata.get("year", "Unknown Year") if metadata else "Unknown Year"
        doi_url = f"https://doi.org/{doi}" if doi else "Unknown DOI"
        
        # Format the forbidden/blocked URLs if any were tracked
        forbidden_section = ""
        if hasattr(self, 'forbidden_urls') and self.forbidden_urls:
            forbidden_section = (
                "-----------------------------------------------------------\n"
                "Exact URLs of Forbidden/Blocked Sites Encountered:\n"
                "-----------------------------------------------------------\n"
            )
            for url, status in self.forbidden_urls:
                forbidden_section += f"- URL:    {url}\n  Status: {status}\n"
            forbidden_section += "\n"
            
            # Print to console
            print(f"\n[WARNING] Download blocked/forbidden. Exact URL(s) of forbidden site(s):")
            for url, status in self.forbidden_urls:
                print(f"  - {url} ({status})")
            print()

        # Build contents
        content = (
            "===========================================================\n"
            "                 PAPER DOWNLOAD ERROR REPORT\n"
            "===========================================================\n\n"
            f"Title:        {title}\n"
            f"Authors:      {authors}\n"
            f"Year:         {year}\n"
            f"DOI:          {doi if doi else 'None'}\n"
            f"Landing Page: {doi_url}\n\n"
            f"{forbidden_section}"
            "-----------------------------------------------------------\n"
            "Download Failure Details:\n"
            "-----------------------------------------------------------\n"
            f"Status:       Download Blocked / Forbidden / Unavailable\n"
            f"Reason:       {reason}\n"
            f"PDF URL:      {pdf_url if pdf_url else 'None found on open-access or mirrors'}\n\n"
            "-----------------------------------------------------------\n"
            "Manual Retrieval Instructions:\n"
            "-----------------------------------------------------------\n"
            "1. Copy and paste the Landing Page URL or any of the Forbidden URLs into your web browser.\n"
            "2. Download the document PDF using your browser session.\n"
            f"3. Place and rename the downloaded file to:\n"
            f"   {os.path.abspath(dest_path)}\n"
        )
        
        try:
            os.makedirs(os.path.dirname(os.path.abspath(txt_path)), exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[OK] Download failed info file created at: {txt_path}")
            return txt_path
        except Exception as e:
            print(f"[ERROR] Failed to save failure info file: {str(e)}")
            return ""
