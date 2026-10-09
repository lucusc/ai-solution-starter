[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]
    $FilePath,
    [switch]
    $Append
)

$values = @($(azd env get-values) | ForEach-Object {
        $name, $value = $_ -split '=', 2
        [PSCustomObject]@{
            name  = $name.Trim()
            value = $value.Trim().Trim('"')
        }
    })

$compressedJson = ConvertTo-Json $values -Depth 10 -Compress

Write-Output "variables=$compressedJson" | Out-File -FilePath $FilePath -Encoding utf8 -Append:$Append -Force