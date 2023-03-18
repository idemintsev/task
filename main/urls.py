from main.views import FilesLoaderView

urls_rules = [
    {'rule': '/files', 'view_func': FilesLoaderView.as_view('files_loader_view'), 'methods': ['POST']},
]
