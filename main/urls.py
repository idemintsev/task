from main.views import FileUploadView, FileDownloadView

urls_rules = [
    {'rule': '/files', 'view_func': FileUploadView.as_view('file_download_view'), 'methods': ['POST']},
    {'rule': '/files/<id>', 'view_func': FileDownloadView.as_view('file_upload_view'), 'methods': ['GET', 'DELETE']},
]
