# Instala a skill edicao-de-cortes no Windows, num comando só (PowerShell):
#
#   irm https://raw.githubusercontent.com/MickaelAlecsander/edicao-de-cortes/main/instalar.ps1 | iex
#
# 1. Instala pelo winget o que faltar: Git, Python 3.12, Node LTS, ffmpeg e Google Chrome.
# 2. Baixa a skill para %USERPROFILE%\.claude\skills\edicao-de-cortes (ou atualiza com git pull, se já existir).
# 3. Roda o scripts\instalar.py: pacotes do Python, playwright-core, modelos (Whisper e MMS_FA), HyperFrames e o autoteste.
# Termina com "pronto para editar". Depois, abrir uma conversa NOVA no Claude Code para a skill aparecer.
# Para testar em outra pasta: $env:EDICAO_DESTINO = "C:\outra\pasta"

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/MickaelAlecsander/edicao-de-cortes"
$Destino = if ($env:EDICAO_DESTINO) { $env:EDICAO_DESTINO } else { Join-Path $env:USERPROFILE ".claude\skills\edicao-de-cortes" }

function Recarrega-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

function Tem($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Instala($id, $nome) {
    if (-not (Tem "winget")) {
        throw "Falta o winget (Instalador de Aplicativos da Microsoft Store). Instale o $nome à mão e rode este script de novo."
    }
    Write-Host "  ... instalando $nome (winget $id)"
    winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements | Out-Host
    Recarrega-Path
}

# o Python de verdade (o "python" da Microsoft Store é só um atalho que abre a loja)
function Acha-Python {
    foreach ($c in @(@("py", "-3.12"), @("py", "-3"), @("python"))) {
        if (Tem $c[0]) {
            try {
                $v = & $c[0] $c[1..9] -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
                if ($v -and [version]$v -ge [version]"3.11") { return , $c }
            } catch {}
        }
    }
    return $null
}

Write-Host "Skill edicao-de-cortes: instalando no Windows"
Write-Host "1 · Programas"
if (-not (Tem "git")) { Instala "Git.Git" "Git" } else { Write-Host "  ok Git" }
if (-not (Acha-Python)) { Instala "Python.Python.3.12" "Python 3.12" } else { Write-Host "  ok Python" }
if (-not (Tem "node")) { Instala "OpenJS.NodeJS.LTS" "Node LTS" } else { Write-Host "  ok Node" }
if (-not (Tem "ffmpeg")) { Instala "Gyan.FFmpeg" "ffmpeg" } else { Write-Host "  ok ffmpeg" }
$chrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe") | Where-Object { Test-Path $_ }
if (-not $chrome) { Instala "Google.Chrome" "Google Chrome" } else { Write-Host "  ok Chrome" }

$py = Acha-Python
if (-not $py) { throw "O Python 3.11+ não apareceu depois da instalação. Feche e abra o PowerShell e rode este script de novo." }
if (-not (Tem "git")) { throw "O Git não apareceu depois da instalação. Feche e abra o PowerShell e rode este script de novo." }

Write-Host "2 · A skill em $Destino"
if (Test-Path (Join-Path $Destino ".git")) {
    git -C $Destino pull --ff-only | Out-Host
} elseif (Test-Path $Destino) {
    throw "A pasta $Destino já existe e não é um clone do GitHub. Mova-a para outro lugar e rode de novo."
} else {
    New-Item -ItemType Directory -Force (Split-Path $Destino) | Out-Null
    git clone $Repo $Destino | Out-Host
}

Write-Host "3 · Pacotes, modelos e autoteste (scripts\instalar.py)"
& $py[0] $py[1..9] (Join-Path $Destino "scripts\instalar.py") @args
if ($LASTEXITCODE -ne 0) { throw "O scripts\instalar.py terminou com o que faltou (lista acima)." }
Write-Host ""
Write-Host "Pronto. Abra uma conversa NOVA no Claude Code para a skill edicao-de-cortes aparecer."
