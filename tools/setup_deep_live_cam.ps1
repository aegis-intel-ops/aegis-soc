
Write-Host ">>> Aegis Deep-Live-Cam Setup <<<" -ForegroundColor Cyan
Write-Host "This script will set up Deep-Live-Cam on your LOCAL Windows machine."

# 1. Clone Repo
if (-not (Test-Path "Deep-Live-Cam")) {
    Write-Host "Cloning Deep-Live-Cam..."
    git clone https://github.com/hacksider/Deep-Live-Cam.git
} else {
    Write-Host "Deep-Live-Cam directory exists. Skipping clone."
}

Set-Location Deep-Live-Cam

# 2. Check Python
$pyVersion = python --version 2>&1
if ($pyVersion -match "3\.10") {
    Write-Host "Python 3.10 detected ($pyVersion)" -ForegroundColor Green
} else {
    Write-Host "WARNING: Python 3.10 is recommended. Detected: $pyVersion" -ForegroundColor Yellow
}

# 3. Create Venv
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# 4. Install Dependencies
Write-Host "Installing dependencies..."
.\venv\Scripts\activate
pip install -r requirements.txt

# 5. Download Models
$modelDir = "models"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir }

$models = @(
    @("GFPGANv1.4.pth", "https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth"),
    @("inswapper_128_fp16.onnx", "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx")
)

foreach ($m in $models) {
    $name = $m[0]
    $url = $m[1]
    $outPath = Join-Path $modelDir $name
    if (-not (Test-Path $outPath)) {
        Write-Host "Downloading $name..."
        Invoke-WebRequest -Uri $url -OutFile $outPath
    } else {
        Write-Host "$name already exists."
    }
}

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "To run:"
Write-Host "1. cd Deep-Live-Cam"
Write-Host "2. .\venv\Scripts\activate"
Write-Host "3. python run.py"
Write-Host "   (Or 'python run.py --execution-provider cuda' if you have NVIDIA GPU)"
