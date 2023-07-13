if (Test-Path ".\build") {
    Remove-Item .\build -Recurse
}
if (Test-Path ".\dist") {
    Remove-Item .\dist -Recurse
}
if (Test-Path ".\po-extractor.spec") {
    Remove-Item .\po-extractor.spec
}
.\venv\Scripts\activate
pyinstaller .\po-extractor.py --onefile --noconsole --add-binary ".\venv\Lib\site-packages\pypdfium2\pdfium.dll;." 
Copy-Item .\po_std_format.xlsx .\dist\po_std_format.xlsx