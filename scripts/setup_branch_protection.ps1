# ==============================================================================
# Setup GitHub Branch Protection Rules via PowerShell & GitHub CLI (gh)
# ==============================================================================
param (
    [string]$Repo = "KrishnakantYadav00/cicdintegratedshortner",
    [string]$Branch = "main"
)

Write-Host "Configuring Branch Protection for $Repo ($Branch)..." -ForegroundColor Cyan

$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghInstalled) {
    Write-Host "[!] GitHub CLI (gh) was not found in PATH." -ForegroundColor Yellow
    Write-Host "Configure branch protection manually in the GitHub Web UI:"
    Write-Host "1. Visit: https://github.com/$Repo/settings/branches"
    Write-Host "2. Click 'Add branch protection rule'"
    Write-Host "3. Branch name pattern: $Branch"
    Write-Host "4. Check 'Require a pull request before merging'"
    Write-Host "5. Check 'Require status checks to pass before merging':"
    Write-Host "     - Require branches to be up to date before merging"
    Write-Host "     - Status checks: 'Lint & Unit Tests', 'Docker Build & Vulnerability Scan'"
    Write-Host "6. Check 'Do not allow bypassing the above settings'"
    Write-Host "7. Click 'Save changes'"
    exit 0
}

$payload = @"
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Lint & Unit Tests",
      "Docker Build & Vulnerability Scan"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
"@

$tempJson = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempJson -Value $payload

try {
    gh api --method PUT -H "Accept: application/vnd.github+json" "/repos/$Repo/branches/$Branch/protection" --input $tempJson
    Write-Host "[✓] Branch protection successfully enabled for $Repo : $Branch!" -ForegroundColor Green
} catch {
    Write-Error "Failed to update branch protection via API: $_"
} finally {
    Remove-Item -Path $tempJson -ErrorAction SilentlyContinue
}
