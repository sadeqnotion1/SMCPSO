#======================================================================================\\\
#============================ cli.py ==================================================\\\
#======================================================================================\\\

import os
import sys
import argparse
from fetcher import PDFFetcher

def main():
    parser = argparse.ArgumentParser(
        description="PDF Fetcher: Automatically search and download research papers by DOI or keyword."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--doi", help="Direct DOI of the paper to download.")
    group.add_argument("-q", "--query", help="Keyword query to search and select papers.")
    
    parser.add_argument(
        "-o", "--out", 
        default="downloads", 
        help="Output folder directory or specific file path (defaults to './downloads/')."
    )

    args = parser.parse_args()
    fetcher = PDFFetcher()

    if args.doi:
        doi = fetcher.clean_doi(args.doi)
        if not doi:
            print("[ERROR] Invalid DOI string provided.")
            sys.exit(1)
            
        # Determine destination path
        if args.out.lower().endswith(".pdf"):
            dest_path = args.out
        else:
            filename = doi.replace("/", "_") + ".pdf"
            dest_path = os.path.join(args.out, filename)
            
        # Retrieve metadata for the report on failure
        print(f"[INFO] Retrieving metadata for DOI: {doi}...")
        meta_results = fetcher.search_crossref(doi, limit=1)
        metadata = meta_results[0] if meta_results else {"title": "Unknown Title", "authors": "Unknown Authors", "year": "Unknown Year"}
        
        print(f"[INFO] Initiating download for DOI: {doi}")
        pdf_url = fetcher.fetch_from_unpaywall(doi)
        if not pdf_url:
            pdf_url = fetcher.fetch_from_scihub(doi)
            
        if pdf_url:
            success = fetcher.download_pdf(pdf_url, dest_path)
            if success:
                print(f"[OK] Done! File saved at: {os.path.abspath(dest_path)}")
                sys.exit(0)
            else:
                fetcher.save_failure_info(
                    dest_path, doi, pdf_url, 
                    "Mirror returned HTTP error, blocked connection, or file is not a valid PDF", 
                    metadata
                )
                sys.exit(1)
        else:
            fetcher.save_failure_info(
                dest_path, doi, "", 
                "No PDF url found on open-access (Unpaywall) or mirrors (Sci-Hub)", 
                metadata
            )
            sys.exit(1)

    elif args.query:
        print(f"[INFO] Searching for papers matching: '{args.query}'...")
        results = fetcher.search_crossref(args.query, limit=5)
        
        if not results:
            print("[INFO] No matches found on Crossref.")
            sys.exit(0)
            
        print("\n--- Search Results ---")
        for i, paper in enumerate(results):
            print(f"[{i + 1}] {paper['title']}")
            print(f"    Authors: {paper['authors']} | Year: {paper['year']}")
            print(f"    DOI: {paper['doi']}\n")
            
        try:
            choice = input("Select a paper number to download (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                print("[INFO] Aborted by user.")
                sys.exit(0)
                
            idx = int(choice) - 1
            if idx < 0 or idx >= len(results):
                print("[ERROR] Invalid selection.")
                sys.exit(1)
                
            selected = results[idx]
            doi = selected["doi"]
            print(f"[INFO] Selected: '{selected['title']}' (DOI: {doi})")
            
            # Determine destination path
            if args.out.lower().endswith(".pdf"):
                dest_path = args.out
            else:
                # Sanitize title to use as filename
                safe_title = "".join(c for c in selected["title"][:50] if c.isalnum() or c in (" ", "_", "-")).rstrip()
                safe_title = safe_title.replace(" ", "_")
                dest_path = os.path.join(args.out, f"{safe_title}.pdf")
                
            pdf_url = fetcher.fetch_from_unpaywall(doi)
            if not pdf_url:
                pdf_url = fetcher.fetch_from_scihub(doi)
                
            if pdf_url:
                success = fetcher.download_pdf(pdf_url, dest_path)
                if success:
                    print(f"[OK] Done! File saved at: {os.path.abspath(dest_path)}")
                    sys.exit(0)
                else:
                    fetcher.save_failure_info(
                        dest_path, doi, pdf_url, 
                        "Mirror returned HTTP error, blocked connection, or file is not a valid PDF", 
                        selected
                    )
                    sys.exit(1)
            else:
                fetcher.save_failure_info(
                    dest_path, doi, "", 
                    "No PDF url found on open-access (Unpaywall) or mirrors (Sci-Hub)", 
                    selected
                )
                sys.exit(1)
                
        except ValueError:
            print("[ERROR] Please enter a valid number.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n[INFO] Aborted by user.")
            sys.exit(0)

if __name__ == "__main__":
    main()
