[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectName,

    [ValidateSet('auto', 'pnpm', 'npm')]
    [string]$PackageManager = 'auto'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PackageManager {
    param([string]$Requested)

    if ($Requested -ne 'auto') {
        return $Requested
    }

    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        return 'pnpm'
    }

    return 'npm'
}

function Install-Packages {
    param(
        [string]$Manager,
        [string[]]$Packages,
        [switch]$Dev
    )

    if (-not $Packages -or $Packages.Count -eq 0) {
        return
    }

    if ($Manager -eq 'pnpm') {
        $args = @('add')
        if ($Dev) { $args += '-D' }
        $args += $Packages
        & pnpm @args
    }
    else {
        $args = @('install')
        if ($Dev) { $args += '-D' }
        $args += $Packages
        & npm @args
    }
}

$resolvedManager = Get-PackageManager -Requested $PackageManager
$nodeVersionText = (& node -v).Trim().TrimStart('v')
$nodeVersion = [version]$nodeVersionText
if ($nodeVersion.Major -lt 18) {
    throw "Node.js 18 or newer is required. Found $nodeVersionText"
}

$viteVersion = if ($nodeVersion.Major -ge 20) { 'latest' } else { '5.4.11' }
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$componentsTarball = Join-Path $scriptDir 'shadcn-components.tar.gz'
if (-not (Test-Path -LiteralPath $componentsTarball)) {
    throw "Missing bundled shadcn component archive: $componentsTarball"
}

Write-Host "Using package manager: $resolvedManager"
Write-Host "Detected Node.js version: $nodeVersionText"

if ($resolvedManager -eq 'pnpm') {
    & pnpm create vite $ProjectName --template react-ts
}
else {
    & npm create vite@latest $ProjectName -- --template react-ts
}

Set-Location -LiteralPath $ProjectName

$indexHtml = Get-Content -Raw -LiteralPath 'index.html'
$indexHtml = [regex]::Replace($indexHtml, '<link rel="icon"[^>]*>\s*', '', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
$indexHtml = [regex]::Replace($indexHtml, '<title>.*?</title>', "<title>$ProjectName</title>")
Set-Content -LiteralPath 'index.html' -Encoding UTF8 -Value $indexHtml

if ($resolvedManager -eq 'pnpm') {
    & pnpm install
    if ($nodeVersion.Major -lt 20) {
        & pnpm add -D "vite@$viteVersion"
    }
}
else {
    & npm install
    if ($nodeVersion.Major -lt 20) {
        & npm install -D "vite@$viteVersion"
    }
}

Install-Packages -Manager $resolvedManager -Dev -Packages @(
    'tailwindcss@3.4.1',
    'postcss',
    'autoprefixer',
    '@types/node',
    'tailwindcss-animate'
)

Install-Packages -Manager $resolvedManager -Packages @(
    'class-variance-authority',
    'clsx',
    'tailwind-merge',
    'lucide-react',
    'next-themes'
)

Set-Content -LiteralPath 'postcss.config.js' -Encoding UTF8 -Value @'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'@

Set-Content -LiteralPath 'tailwind.config.js' -Encoding UTF8 -Value @'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
'@

Set-Content -LiteralPath 'src\index.css' -Encoding UTF8 -Value @'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 3.9%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 96.1%;
    --secondary-foreground: 0 0% 9%;
    --muted: 0 0% 96.1%;
    --muted-foreground: 0 0% 45.1%;
    --accent: 0 0% 96.1%;
    --accent-foreground: 0 0% 9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 89.8%;
    --input: 0 0% 89.8%;
    --ring: 0 0% 3.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
  }
}

@layer base {
  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground;
  }
}
'@

& node -e "const fs=require('fs');const path='tsconfig.json';const config=JSON.parse(fs.readFileSync(path,'utf8'));config.compilerOptions=config.compilerOptions||{};config.compilerOptions.baseUrl='.';config.compilerOptions.paths={'@/*':['./src/*']};fs.writeFileSync(path,JSON.stringify(config,null,2));"

& node -e "const fs=require('fs');const path='tsconfig.app.json';const content=fs.readFileSync(path,'utf8');const noLineComments=content.split('\n').filter(line=>!line.trim().startsWith('//')).join('\n');const normalized=noLineComments.replace(/\/\*[\s\S]*?\*\//g,'').replace(/,(\s*[}\]])/g,'$1');const config=JSON.parse(normalized);config.compilerOptions=config.compilerOptions||{};config.compilerOptions.baseUrl='.';config.compilerOptions.paths={'@/*':['./src/*']};fs.writeFileSync(path,JSON.stringify(config,null,2));"

Set-Content -LiteralPath 'vite.config.ts' -Encoding UTF8 -Value @'
import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
'@

Install-Packages -Manager $resolvedManager -Packages @(
    '@radix-ui/react-accordion',
    '@radix-ui/react-aspect-ratio',
    '@radix-ui/react-avatar',
    '@radix-ui/react-checkbox',
    '@radix-ui/react-collapsible',
    '@radix-ui/react-context-menu',
    '@radix-ui/react-dialog',
    '@radix-ui/react-dropdown-menu',
    '@radix-ui/react-hover-card',
    '@radix-ui/react-label',
    '@radix-ui/react-menubar',
    '@radix-ui/react-navigation-menu',
    '@radix-ui/react-popover',
    '@radix-ui/react-progress',
    '@radix-ui/react-radio-group',
    '@radix-ui/react-scroll-area',
    '@radix-ui/react-select',
    '@radix-ui/react-separator',
    '@radix-ui/react-slider',
    '@radix-ui/react-slot',
    '@radix-ui/react-switch',
    '@radix-ui/react-tabs',
    '@radix-ui/react-toast',
    '@radix-ui/react-toggle',
    '@radix-ui/react-toggle-group',
    '@radix-ui/react-tooltip',
    'sonner',
    'cmdk',
    'vaul',
    'embla-carousel-react',
    'react-day-picker',
    'react-resizable-panels',
    'date-fns',
    'react-hook-form',
    '@hookform/resolvers',
    'zod'
)

if (Get-Command tar -ErrorAction SilentlyContinue) {
    & tar -xzf $componentsTarball -C 'src'
}
else {
    Write-Warning 'tar was not found; continuing without pre-bundled shadcn components.'
}

Set-Content -LiteralPath 'components.json' -Encoding UTF8 -Value @'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
'@

Write-Host ''
Write-Host 'Setup complete.'
Write-Host "Project: $ProjectName"
Write-Host 'Run the app with your package manager, then bundle it with bundle-static-web.ps1 when ready.'
