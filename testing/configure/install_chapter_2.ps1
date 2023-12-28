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
RunScript '.\sysmon_install_in_sysvol.ps1'
RunScript '.\sysmon_import_gpo.ps1 -directory lme'
RunScript '.\sysmon_gpo_update_vars.ps1'
RunScript '.\sysmon_link_gpo.ps1'
