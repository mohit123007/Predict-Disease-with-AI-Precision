def create_pdf_report(prediction_result: dict, out_path: str):
    """Stub PDF generator. Use ReportLab or FPDF in real implementation."""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('PDF placeholder for prediction:\n')
        f.write(str(prediction_result))
    return out_path
