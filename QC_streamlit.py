import streamlit as st
import pandas as pd
import csv
from io import BytesIO

# -----------------------------
# LOGIC FUNCTION (same as GUI)
# -----------------------------
def process_files(csv_file, xlsx_file, job_name, job_date):
    csv_data = []
    try:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader, None)
        for row in reader:
            clean_rfid = row[0].replace('-', '')
            csv_data.append(clean_rfid)
    except Exception as e:
        return None, f"Error reading CSV file:\n{e}"

    rfid_count = len(csv_data)

    try:
        df_excel = pd.read_excel(xlsx_file)
    except Exception as e:
        return None, f"Error reading Excel file:\n{e}"

    if df_excel.shape[1] < 2:
        return None, "Excel file does not contain enough columns."

    df_excel['RFID_CLEAN'] = df_excel.iloc[:, 1].astype(str).str.replace('-', '', regex=False)

    df_matches = df_excel[df_excel['RFID_CLEAN'].isin(csv_data)].copy()

    cols_to_drop = []
    if df_matches.shape[1] > 2:
        cols_to_drop.append(df_matches.columns[2])
    if df_matches.shape[1] > 3:
        cols_to_drop.append(df_matches.columns[3])

    df_matches.drop(columns=cols_to_drop, inplace=True)
    df_matches.drop(columns=['RFID_CLEAN'], inplace=True)

    summary = []
    summary.append("Composite Piping Technology, LLC")
    summary.append("Production and Scanned RFID Comparison")
    summary.append("-----------------------------------")
    summary.append(f"{job_name}   {job_date}")
    summary.append("-----------------------------------")

    for _, row in df_matches.iterrows():
        summary.append(f"{row.iloc[0]}   {row.iloc[1]}")

    summary.append("-----------------------------------")
    summary.append(f"Total RFIDs Scanned: {rfid_count}")
    summary.append(f"Total Matches Found: {len(df_matches)}")
    summary.append("-----------------------------------")

    return df_matches, "\n".join(summary)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("Composite Piping Technology, LLC")
st.header("RFID Scanlog vs Production Sheet Comparison Tool")

job_name = st.text_input("Job Name")
job_date = st.date_input("Job Date")

csv_file = st.file_uploader("Upload CSV Scanlog", type=["csv"])
xlsx_file = st.file_uploader("Upload Excel Production File", type=["xlsx"])

if st.button("Run Comparison"):
    if not job_name or not csv_file or not xlsx_file:
        st.error("Please provide all inputs.")
    else:
        df_output, summary_text = process_files(
            csv_file,
            xlsx_file,
            job_name,
            job_date.strftime("%d/%B/%Y")
        )

        if df_output is None:
            st.error(summary_text)
        else:
            st.success("Comparison complete.")
            st.text(summary_text)

            # Download output Excel
            output = BytesIO()
            df_output.to_excel(output, index=False)
            st.download_button(
                "Download Output Excel",
                output.getvalue(),
                file_name=f"CPT_{job_name.replace(' ', '_')}.xlsx"
            )
