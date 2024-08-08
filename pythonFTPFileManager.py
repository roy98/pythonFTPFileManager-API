from flask import Flask, request, jsonify
import ftplib
import os
from config import FTP_CONFIG

app = Flask(__name__)

# Configuration FTP
FTP_HOST = FTP_CONFIG['host']
FTP_PORT = FTP_CONFIG['port']
FTP_USER = FTP_CONFIG['user']
FTP_PASS = FTP_CONFIG['password']

def connect_ftp():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        ftp.login(FTP_USER, FTP_PASS)
        return ftp
    except ftplib.all_errors as e:
        print(f"Failed to connect to FTP: {e}")
        return None

@app.route('/file-info', methods=['GET'])
def file_info():
    path = request.args.get('path')
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    ftp = connect_ftp()
    
    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        file_size = ftp.size(path)
        return jsonify({
            "exists": True,
            "name": os.path.basename(path),
            "extension": os.path.splitext(path)[1],
            "size": file_size,
            "path": path,
        })
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            return jsonify({"exists": False, "path": path}), 404
        else:
            return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/list-files', methods=['GET'])
def list_files():
    directory = request.args.get('directory')
    
    if not directory:
        return jsonify({"error": "Directory path is required"}), 400
    
    ftp = connect_ftp()
    
    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        files = ftp.nlst()
        file_list = [f for f in files if '.' in f]  # Simple check for files
        return jsonify(file_list)
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/list-folders', methods=['GET'])
def list_folders():
    directory = request.args.get('directory')
    
    if not directory:
        return jsonify({"error": "Directory path is required"}), 400
    
    ftp = connect_ftp()
    
    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        items = ftp.nlst()
        folders = []
        for item in items:
            try:
                ftp.cwd(item)
                folders.append(item)
                ftp.cwd('..')  # Navigate back to parent directory
            except ftplib.error_perm:
                continue
        return jsonify(folders)
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/upload-file', methods=['POST'])
def upload_file():
    directory = request.form.get('directory')
    file = request.files.get('file')
    
    if not directory or not file:
        return jsonify({"error": "Directory and file are required"}), 400
    
    ftp = connect_ftp()

    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        ftp.storbinary(f'STOR {file.filename}', file.stream)
        return jsonify({"message": "File uploaded successfully", "filename": file.filename})
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/create-folder', methods=['POST'])
def create_folder():
    directory = request.form.get('directory')
    folder_name = request.form.get('folder_name')
    
    if not directory or not folder_name:
        return jsonify({"error": "Directory and folder_name are required"}), 400
    
    ftp = connect_ftp()

    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        ftp.mkd(folder_name)
        return jsonify({"message": f"Folder '{folder_name}' created successfully"})
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/delete-file', methods=['DELETE'])
def delete_file():
    directory = request.form.get('directory')
    filename = request.form.get('filename')
    
    if not directory or not filename:
        return jsonify({"error": "Directory and filename are required"}), 400
    
    ftp = connect_ftp()

    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        ftp.delete(filename)
        return jsonify({"message": f"File '{filename}' deleted successfully"})
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

@app.route('/delete-folder', methods=['DELETE'])
def delete_folder():
    directory = request.form.get('directory')
    folder_name = request.form.get('folder_name')
    force_deletion = request.form.get('force_deletion', 'false').lower() == 'true'
    
    if not directory or not folder_name:
        return jsonify({"error": "Directory and folder_name are required"}), 400
    
    ftp = connect_ftp()

    if ftp is None:
        return jsonify({"error": "Failed to connect to the FTP server"}), 500

    try:
        ftp.cwd(directory)
        ftp.cwd(folder_name)
        items = ftp.nlst()
        
        if items and not force_deletion:
            return jsonify({"error": "Folder is not empty. Use force_deletion to delete non-empty folders."}), 400
        
        if force_deletion:
            for item in items:
                try:
                    ftp.delete(item)
                except ftplib.error_perm:
                    ftp.cwd(item)
                    sub_items = ftp.nlst()
                    for sub_item in sub_items:
                        ftp.delete(sub_item)
                    ftp.cwd('..')
                    ftp.rmd(item)
        
        ftp.cwd('..')
        ftp.rmd(folder_name)
        return jsonify({"message": f"Folder '{folder_name}' deleted successfully"})
    except ftplib.all_errors as e:
        return jsonify({"error": str(e)}), 500
    finally:
        ftp.quit()

if __name__ == '__main__':
    app.run(debug=False)
