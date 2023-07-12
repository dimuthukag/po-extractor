.\venv\Scripts\activate
pyinstaller .\po-extractor.py --onefile --noconsole --add-binary ".\venv\Lib\site-packages\pypdfium2\pdfium.dll;." 
Copy-Item .\po_std_format.xlsx .\dist\po_std_format.xlsx