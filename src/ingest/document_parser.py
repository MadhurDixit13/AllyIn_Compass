import fitz  # PyMuPDF
import email
import os
import json

def parse_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = "".join([page.get_text() for page in doc])
    return {"type": "pdf", "file": os.path.basename(file_path), "text": text}

def parse_eml(file_path):
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f)
        subject = msg.get("Subject", "")
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

    return {"type": "email", "file": os.path.basename(file_path), "subject": subject, "body": body}

def parse_all_files(input_folder, output_path="../../data/unstructured/parsed.jsonl"):
    with open(output_path, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(input_folder):
            path = os.path.join(input_folder, filename)
            if filename.endswith(".pdf"):
                doc = parse_pdf(path)
            elif filename.endswith(".eml"):
                doc = parse_eml(path)
            else:
                continue
            json.dump(doc, outfile)
            outfile.write("\n")

    print(f"Parsed files written to {output_path}")

if __name__ == "__main__":
    parse_all_files("../../data/unstructured")
# This script parses PDF and EML files from a specified folder and writes the parsed content to a JSONL file.
# It uses PyMuPDF for PDF parsing and the email module for EML files.