./venv/Scripts/activate
Write-Host -ForegroundColor Blue "Activating virtual environment"
Write-Host -ForegroundColor Blue "Building executable"
pyinstaller OcrAutomation.spec --version-file = version.txt -y
Write-Host -ForegroundColor Blue "Deactivating virtual environment"
Write-Host -ForegroundColor DarkGreen "Done!"
deactivate
