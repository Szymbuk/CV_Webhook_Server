import base64
import os

def save_bytes_as_pdf(path,bytes_file,file_name):
    if path:
        os.makedirs(path, exist_ok=True)
    else:
        path = "cv_files"
        os.makedirs(path, exist_ok=True)

    if not file_name.endswith(".pdf"):
        file_name = f"{file_name}.pdf"

    full_path = f"{path}/{file_name}"

    pdf = base64.b64decode(bytes_file)
    with open(full_path, "wb") as f:
        f.write(pdf)

    return full_path

def get_pdf_from_bytes(bytes_file):
    return base64.b64decode(bytes_file)


def get_bytes_from_pdf(pdf_path):
    with  open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        b64_bytes = base64.b64encode(pdf_bytes)
    return b64_bytes.decode('utf-8')



# if __name__ == '__main__':
#     bytes = get_bytes_from_pdf("cv_files/egzamin_mownit.pdf")
#     print(bytes)
#     save_bytes_as_pdf("cv_files",bytes,"nowy.pdf")
