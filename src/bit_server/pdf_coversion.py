import base64

def save_bytes_as_pdf(path,bytes_file,file_name):
    pdf = base64.b64decode(bytes_file)
    with  open(f"{path}/{file_name}.pdf", "wb") as f:
        f.write(pdf)


def get_pdf_from_bytes(bytes_file):
    return base64.b64decode(bytes_file)
