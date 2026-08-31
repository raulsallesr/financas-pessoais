[CmdletBinding()]
param(
    [switch]$CheckSyntaxOnly,
    [string]$FlowPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$mobileRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$appConfig = Get-Content -Raw -LiteralPath (Join-Path $mobileRoot "app.json") |
    ConvertFrom-Json
$appId = [string]$appConfig.expo.android.package
$expectedVersion = [string]$appConfig.expo.version
$expectedVersionCode = [string]$appConfig.expo.android.versionCode
$portableRoot = Join-Path $env:LOCALAPPDATA "focuslens-tools"

function Resolve-ToolExecutable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [string]$FileName,
        [Parameter(Mandatory = $true)]
        [string]$CommandName,
        [string]$ExplicitRoot,
        [string]$DefaultRoot
    )

    if ($ExplicitRoot) {
        if (-not (Test-Path -LiteralPath $ExplicitRoot -PathType Container)) {
            throw "$Label não encontrado no caminho configurado: $ExplicitRoot"
        }
        $explicitMatch = Get-ChildItem -LiteralPath $ExplicitRoot -Filter $FileName `
            -File -Recurse | Sort-Object FullName | Select-Object -First 1
        if (-not $explicitMatch) {
            throw "$Label não contém $FileName em: $ExplicitRoot"
        }
        return $explicitMatch.FullName
    }

    if (Test-Path -LiteralPath $DefaultRoot -PathType Container) {
        $portableMatch = Get-ChildItem -LiteralPath $DefaultRoot -Filter $FileName `
            -File -Recurse | Sort-Object FullName | Select-Object -First 1
        if ($portableMatch) {
            return $portableMatch.FullName
        }
    }

    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw "$Label não encontrado. Consulte mobile/tests/README.md para preparar o ambiente."
}

$javaOverride = $env:FOCUSLENS_JAVA_HOME
if (-not $javaOverride) {
    $javaOverride = $env:JAVA_HOME
}

$javaExe = Resolve-ToolExecutable -Label "Java 17+" -FileName "java.exe" `
    -CommandName "java.exe" -ExplicitRoot $javaOverride `
    -DefaultRoot (Join-Path $portableRoot "temurin-17")
$maestroBat = Resolve-ToolExecutable -Label "Maestro CLI" -FileName "maestro.bat" `
    -CommandName "maestro.bat" -ExplicitRoot $env:FOCUSLENS_MAESTRO_HOME `
    -DefaultRoot (Join-Path $portableRoot "maestro")
$adbExe = Resolve-ToolExecutable -Label "Android Debug Bridge" -FileName "adb.exe" `
    -CommandName "adb.exe" -ExplicitRoot $env:FOCUSLENS_ANDROID_PLATFORM_TOOLS `
    -DefaultRoot (Join-Path $portableRoot "android-platform-tools")

$javaBin = Split-Path -Parent $javaExe
$javaHome = Split-Path -Parent $javaBin
$maestroBin = Split-Path -Parent $maestroBat
$adbBin = Split-Path -Parent $adbExe
$env:JAVA_HOME = $javaHome
$env:Path = "$javaBin;$maestroBin;$adbBin;$env:Path"
$env:MAESTRO_CLI_NO_ANALYTICS = "1"
$env:MAESTRO_CLI_ANALYSIS_NOTIFICATION_DISABLED = "true"
$env:MAESTRO_EXIT_CONSOLE = "true"
$env:DEBUG = $null

$maestroMutex = [System.Threading.Mutex]::new(
    $false,
    "Local\FocusLensMaestroCli"
)
$mutexAcquired = $false
try {
    $mutexAcquired = $maestroMutex.WaitOne(0)
} catch [System.Threading.AbandonedMutexException] {
    $mutexAcquired = $true
}
if (-not $mutexAcquired) {
    $maestroMutex.Dispose()
    throw "Outra execução local do Maestro já está em andamento."
}

function Invoke-Maestro {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $maestroBat @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Maestro falhou com código $LASTEXITCODE."
    }
}

try {
$flowsRoot = Join-Path $mobileRoot "e2e\maestro\flows"
if ($FlowPath) {
    $candidate = $FlowPath
    if (-not [System.IO.Path]::IsPathRooted($candidate)) {
        $candidate = Join-Path $mobileRoot $candidate
    }
    $flows = @((Resolve-Path -LiteralPath $candidate).Path)
} else {
    $flows = @(Get-ChildItem -LiteralPath $flowsRoot -Filter "*.yaml" -File |
        Sort-Object Name | Select-Object -ExpandProperty FullName)
}

if ($flows.Count -eq 0) {
    throw "Nenhum fluxo Maestro encontrado em $flowsRoot"
}

foreach ($flow in $flows) {
    Invoke-Maestro -Arguments @("check-syntax", $flow)
    Write-Output "Sintaxe aprovada: $(Split-Path -Leaf $flow)"
}

if ($CheckSyntaxOnly) {
    Write-Output "Gate de sintaxe concluído; nenhum dispositivo foi acionado."
    return
}

& $adbExe start-server | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível iniciar o ADB."
}

$deviceLines = @(& $adbExe devices | Select-Object -Skip 1 |
    Where-Object { $_ -match "\S" })
$devices = @($deviceLines | ForEach-Object {
    $parts = $_ -split "\s+"
    [pscustomobject]@{
        Id = $parts[0]
        Status = $parts[1]
    }
})
$deviceId = $env:FOCUSLENS_ANDROID_DEVICE

if ($deviceId) {
    $selected = @($devices | Where-Object { $_.Id -eq $deviceId })
    if ($selected.Count -ne 1 -or $selected[0].Status -ne "device") {
        throw "O dispositivo configurado em FOCUSLENS_ANDROID_DEVICE não está autorizado."
    }
} else {
    $authorized = @($devices | Where-Object { $_.Status -eq "device" })
    $unauthorized = @($devices | Where-Object { $_.Status -eq "unauthorized" })
    if ($unauthorized.Count -gt 0) {
        throw "Há Android conectado aguardando autorização de depuração USB no aparelho."
    }
    if ($authorized.Count -eq 0) {
        throw "Nenhum Android autorizado foi encontrado. Conecte o aparelho por USB e tente novamente."
    }
    if ($authorized.Count -gt 1) {
        throw "Há mais de um Android autorizado. Defina FOCUSLENS_ANDROID_DEVICE para selecionar um."
    }
    $deviceId = $authorized[0].Id
}

$adbDeviceArgs = @("-s", $deviceId)
$packagePath = @(& $adbExe @adbDeviceArgs shell pm path $appId 2>$null)
if ($LASTEXITCODE -ne 0 -or -not ($packagePath -match "^package:")) {
    throw "O app $appId não está instalado no dispositivo autorizado."
}

$packageInfo = @(& $adbExe @adbDeviceArgs shell dumpsys package $appId)
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível ler a versão instalada de $appId."
}
$packageText = $packageInfo -join "`n"
$versionNameMatch = [regex]::Match($packageText, "(?m)^\s*versionName=(\S+)")
$versionCodeMatch = [regex]::Match($packageText, "(?m)^\s*versionCode=(\d+)")
if (-not $versionNameMatch.Success -or -not $versionCodeMatch.Success) {
    throw "O ADB não retornou versionName/versionCode para $appId."
}

$installedVersion = $versionNameMatch.Groups[1].Value
$installedVersionCode = $versionCodeMatch.Groups[1].Value
if ($installedVersion -ne $expectedVersion -or
    $installedVersionCode -ne $expectedVersionCode) {
    throw "Build incompatível: instalado $installedVersion/$installedVersionCode; esperado $expectedVersion/$expectedVersionCode."
}

$androidRelease = (& $adbExe @adbDeviceArgs shell getprop ro.build.version.release).Trim()
$androidBuild = (& $adbExe @adbDeviceArgs shell getprop ro.build.id).Trim()
Write-Output "Dispositivo autorizado: Android $androidRelease ($androidBuild)."
Write-Output "Build aprovado para teste: $appId $installedVersion/$installedVersionCode."

$maestroArgs = @("--device=$deviceId", "test")
if ($FlowPath) {
    $maestroArgs += $flows[0]
} else {
    $maestroArgs += (Join-Path $mobileRoot "e2e\maestro")
}

Push-Location $mobileRoot
try {
    Invoke-Maestro -Arguments $maestroArgs
} finally {
    Pop-Location
}

Write-Output "Fluxos Maestro concluídos no build $installedVersion/$installedVersionCode."
} finally {
    if ($mutexAcquired) {
        $maestroMutex.ReleaseMutex()
    }
    $maestroMutex.Dispose()
}
