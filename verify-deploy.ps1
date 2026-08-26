# verify-deploy.ps1 - confirm a push actually reached the live site.
#
# Run AFTER `git push`, once Cloudflare Pages has built (~2 min).
#   .\verify-deploy.ps1
#
# Notes for future edits:
#   - Use curl.exe, NOT curl. In PowerShell `curl` is an alias for
#     Invoke-WebRequest and does not accept -s/-o/-w.
#   - curl.exe output arrives as an ARRAY of lines, so join it before regexing.
#   - Do not use $home as a variable name; it is read-only in PowerShell.

$ErrorActionPreference = "Stop"
$site = "https://pursueufotracker.com"

# Pages that only exist after the Drop 05 deploy.
$paths = @(
    "/drops/2026-08-07-drop-05",
    "/files/eop-uap-d001-nasc-inquiry-into-bahia-brazil-incident-november-13-1963",
    "/files/fbi-uap-pr007-slow-moving-objects-2026"
)

Write-Output "Checking $site ..."
Write-Output ""
$fail = 0
foreach ($p in $paths) {
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 25 "$site$p"
    if ($code -ne "200") { $fail++ }
    "{0}  {1,-6} {2}" -f $(if ($code -eq "200") { "OK  " } else { "FAIL" }), $code, $p
}

# The archive count the site advertises, on two independent surfaces.
$hp = (curl.exe -s --max-time 25 "$site/") -join " "
$m  = [regex]::Match($hp, 'ALL (\d+) FILES')
$hpN = if ($m.Success) { $m.Groups[1].Value } else { "?" }

$lt = (curl.exe -s --max-time 25 "$site/llms.txt") -join " "
$m2 = [regex]::Match($lt, 'all (\d+) files')
$ltN = if ($m2.Success) { $m2.Groups[1].Value } else { "?" }

Write-Output ""
"{0}  homepage advertises {1} files (want 375)" -f $(if ($hpN -eq "375") { "OK  " } else { "FAIL" }), $hpN
"{0}  llms.txt advertises {1} files (want 375)" -f $(if ($ltN -eq "375") { "OK  " } else { "FAIL" }), $ltN
if ($hpN -ne "375") { $fail++ }
if ($ltN -ne "375") { $fail++ }

Write-Output ""
if ($fail -eq 0) {
    Write-Output "DEPLOY VERIFIED - Drop 05 is live. Safe to post the Reddit thread."
} else {
    Write-Output "$fail check(s) failed."
    Write-Output "If you just pushed, Cloudflare may still be building - wait 60s and re-run."
    Write-Output "If it still fails, the push did not land: run  git status  and  git log --oneline -1"
}
