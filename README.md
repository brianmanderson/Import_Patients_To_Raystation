# Import_Patients_To_Raystation

Tools for bulk-importing many patients' DICOM data into RayStation. A standalone prep GUI cleans up a folder tree of exported DICOM outside RayStation, then a script run inside RayStation walks the prepared folders and imports each patient automatically — avoiding importing them one at a time by hand.

Not actively maintained (last updated 2021).

## How it works

**Stage 1 — prep (outside RayStation):** run `Prep_Dicom_GUI.py` (or the bundled `Prep_Dicom_GUI.exe`) and select the parent folder containing per-patient DICOM folders.

- `Prep_dicom_UID.py` reads each series with pydicom (multithreaded) and regenerates UIDs, with checkbox options for overlapping images and multiphase liver CTs. It writes `UID_val.txt` and `MRN_val.txt` marker files into each patient folder.
- `Dir_Listing_CT_RT_Files.py` sorts folders into images (CT/MR) vs RT/plan/dose, copies one query file per patient into a `query_file` subfolder, and writes `RayStation_Paths.txt` to the output folder: image folder paths on the top row, everything else (RT structures, plans, dose) on the bottom.

**Stage 2 — import (inside RayStation):** run `Import_Patient_Data_To_Raystation.py` from the RayStation scripting environment. For each prepared folder it reads the MRN/UID markers, queries the RayStation `PatientDB` (falling back to the index service), and imports the patient or adds the series to an existing patient. Folders are stamped with `imported.txt` / `running.txt` so re-runs skip anything already done.

## Requirements

- Prep side: Python 3 with `pydicom` (tkinter GUI), or use the prebuilt `.exe`
- Import side: RayStation scripting environment (`connect` module, IronPython/.NET)
