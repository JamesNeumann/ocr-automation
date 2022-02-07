import glob

from rich.traceback import install

from utils.edit_metadata import set_standard_metadata

if __name__ == '__main__':
    install(show_locals=True)

    # app = QApplication(sys.argv)

    # window = MainWindow()
    # window.show()

    # app.exec()

    for file in glob.glob('./files/metadata/*.pdf'):
        set_standard_metadata(file)
