param (
    [Parameter(
        HelpMessage="Path to the configuration directory. Default is 'C:\lme\configure'."
    )]
    [string]$configurePath = "C:\lme\configure"
)

# Exit the script on any error
$ErrorActionPreference = 'Stop'

# Function to run a script and check for failure
function RunScript {
    param (
        [string]$scriptPath
    )

    & $scriptPath
    if ($LASTEXITCODE -ne 0 -or $?) {
        Write-Error "Script failed: $scriptPath"
        exit $LASTEXITCODE
    }
}

# Change directory to the configure directory
Set-Location -Path $configurePath

# Run the scripts and check for failure
RunScript '.\copy_files\create_lme_directory.ps1'
RunScript '.\download_files.ps1 -directory lme'
RunScript '.\wec_import_gpo.ps1 -directory lme'
RunScript '.\wec_gpo_update_server_name.ps1'
RunScript '.\create_ou.ps1'
RunScript '.\wec_link_gpo.ps1'
RunScript '.\wec_service_provisioner.ps1'

# Run the wevtutil and wecutil commands
wevtutil set-log ForwardedEvents /q:true /e:true
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
wecutil rs lme
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
wecutil gr lme
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Run the move_computers_to_ou script
RunScript '.\move_computers_to_ou.ps1'
