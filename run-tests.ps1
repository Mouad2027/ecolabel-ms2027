# Script PowerShell pour tester tous les microservices
# Run all tests for EcoLabel-MS2027 project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing EcoLabel-MS2027 Microservices" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    "parser-produit",
    "nlp-ingredients", 
    "lca-lite",
    "scoring",
    "provenance"
)

$totalPassed = 0
$totalFailed = 0
$results = @()

foreach ($service in $services) {
    Write-Host "Testing $service..." -ForegroundColor Yellow
    
    $testPath = Join-Path $PSScriptRoot $service "tests"
    
    if (Test-Path $testPath) {
        Push-Location (Join-Path $PSScriptRoot $service)
        
        # Install dependencies if needed
        if (Test-Path "requirements.txt") {
            Write-Host "  Installing dependencies..." -ForegroundColor Gray
            $null = python -m pip install -r requirements.txt -q 2>&1
        }
        
        # Run tests
        $testOutput = python -m pytest tests/ -v --tb=short 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-Host "  ✓ Tests passed" -ForegroundColor Green
            $results += [PSCustomObject]@{
                Service = $service
                Status = "PASSED"
                Color = "Green"
            }
            $totalPassed++
        } else {
            Write-Host "  ✗ Tests failed" -ForegroundColor Red
            $results += [PSCustomObject]@{
                Service = $service
                Status = "FAILED"
                Color = "Red"
            }
            $totalFailed++
            Write-Host $testOutput -ForegroundColor DarkGray
        }
        
        Pop-Location
    } else {
        Write-Host "  ! No tests found" -ForegroundColor DarkYellow
        $results += [PSCustomObject]@{
            Service = $service
            Status = "NO TESTS"
            Color = "DarkYellow"
        }
    }
    
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

foreach ($result in $results) {
    Write-Host "  $($result.Service): $($result.Status)" -ForegroundColor $result.Color
}

Write-Host ""
Write-Host "Total: $totalPassed passed, $totalFailed failed" -ForegroundColor Cyan

if ($totalFailed -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    exit 1
}

