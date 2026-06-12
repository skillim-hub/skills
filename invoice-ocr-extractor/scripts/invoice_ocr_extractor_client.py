#!/usr/bin/env python3
from invoice_ocr_extractor.client import *

if __name__ == "__main__":
    import argparse
    from invoice_ocr_extractor import InvoiceOCRExtractor
    parser = argparse.ArgumentParser(description="Extract invoice fields from an OCR text file.")
    parser.add_argument("path")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(InvoiceOCRExtractor().extract_from_file(args.path).to_json(indent=2 if args.pretty else None))
