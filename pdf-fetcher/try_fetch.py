#======================================================================================\\\
#============================ try_fetch.py ============================================\\\
#======================================================================================\\\

import os
from fetcher import PDFFetcher

def main():
    fetcher = PDFFetcher()
    out_dir = "E:/University/SMC-PSO-beta/references/discussed_sources"
    
    # 1. Moreno (2008) paper by DOI
    print("\n=== Attempting to download Moreno (2008) ===")
    moreno_doi = "10.1109/CDC.2008.4739356"
    dest_moreno = os.path.join(out_dir, "Moreno2008_Lyapunov_STA.pdf")
    
    fetcher.reset()
    # Try to search metadata first
    meta_results = fetcher.search_crossref(moreno_doi, limit=1)
    metadata = meta_results[0] if meta_results else {
        "title": "Lyapunov design of multi-input sliding mode control",
        "authors": "J. A. Moreno",
        "year": "2008"
    }
    
    pdf_url = fetcher.fetch_from_unpaywall(moreno_doi)
    if not pdf_url:
        pdf_url = fetcher.fetch_from_scihub(moreno_doi)
    
    if pdf_url:
        success = fetcher.download_pdf(pdf_url, dest_moreno)
        print(f"Moreno download status: {success}")
        if not success:
            fetcher.save_failure_info(
                dest_moreno, moreno_doi, pdf_url, 
                "Download failed or file was invalid PDF (Forbidden or Paywalled)", 
                metadata
            )
    else:
        print("Moreno PDF URL could not be found.")
        fetcher.save_failure_info(
            dest_moreno, moreno_doi, "", 
            "No PDF url found on open-access (Unpaywall) or mirrors (Sci-Hub)", 
            metadata
        )

    # 2. Prasad (2012) paper download
    print("\n=== Attempting to download Prasad (2012) ===")
    prasad_doi = "10.1109/ams.2012.21"
    dest_prasad = os.path.join(out_dir, "Prasad2012_Inverted_Pendulum_LQR.pdf")
    
    # Clean up previous incorrect PDF/txt if it exists
    for ext in [".pdf", ".txt"]:
        path_to_clean = os.path.splitext(dest_prasad)[0] + ext
        if os.path.exists(path_to_clean):
            try:
                os.remove(path_to_clean)
                print(f"[INFO] Cleared previous file at: {path_to_clean}")
            except Exception as e:
                print(f"[WARNING] Could not delete file {path_to_clean}: {str(e)}")
                print("[INFO] Please close this file if it is open in another program.")

    # Also clean up the old 2014 file path if it exists
    old_prasad_base = os.path.join(out_dir, "Prasad2014_DIP_Modeling")
    for ext in [".pdf", ".txt"]:
        old_path = old_prasad_base + ext
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"[INFO] Cleared old 2014 file at: {old_path}")
            except Exception as e:
                print(f"[WARNING] Could not delete old 2014 file {old_path}: {str(e)}")
        
    prasad_meta = {
        "title": "Modelling and Simulation for Optimal Control of Nonlinear Inverted Pendulum Dynamical System Using PID Controller and LQR",
        "authors": "Lal Bahadur Prasad, Barjeev Tyagi, Hari Om Gupta",
        "year": "2012"
    }
    
    fetcher.reset()
    meta_results = fetcher.search_crossref(prasad_doi, limit=1)
    metadata = meta_results[0] if meta_results else prasad_meta
    
    pdf_url = fetcher.fetch_from_unpaywall(prasad_doi)
    if not pdf_url:
        pdf_url = fetcher.fetch_from_scihub(prasad_doi)
        
    if pdf_url:
        success = fetcher.download_pdf(pdf_url, dest_prasad)
        print(f"Prasad download status: {success}")
        if not success:
            fetcher.save_failure_info(
                dest_prasad, prasad_doi, pdf_url,
                "Download failed or file was invalid PDF (Forbidden or Paywalled)",
                metadata
            )
    else:
        print("Prasad PDF URL could not be found.")
        fetcher.save_failure_info(
            dest_prasad, prasad_doi, "",
            "No PDF url found on open-access (Unpaywall) or mirrors (Sci-Hub)",
            metadata
        )

    # 3. Clean up legacy Oklahoma State University (2013) files
    print("\n=== Cleaning up legacy OSU Thesis (2013) files ===")
    old_osu_base = os.path.join(out_dir, "OkstateThesis2013_DIP_SMC")
    for ext in [".pdf", ".txt"]:
        old_path = old_osu_base + ext
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"[INFO] Cleared old OSU Thesis file at: {old_path}")
            except Exception as e:
                print(f"[WARNING] Could not delete old OSU Thesis file {old_path}: {str(e)}")

if __name__ == "__main__":
    main()
