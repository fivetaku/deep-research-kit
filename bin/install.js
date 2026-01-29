#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const RED = '\x1b[31m';
const NC = '\x1b[0m';

const packageRoot = path.resolve(__dirname, '..');
const targetDir = process.cwd();

console.log(`${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
console.log(`${CYAN}  Deep Research - Installation${NC}`);
console.log(`${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
console.log();

function parseArgs(argv) {
  const args = argv.slice(2);
  const flags = new Set(args);

  const targetIndex = args.indexOf('--target');
  let target = 'auto';
  if (targetIndex !== -1 && args[targetIndex + 1]) {
    target = args[targetIndex + 1];
  } else if (flags.has('--global')) {
    target = 'global';
  } else if (flags.has('--project')) {
    target = 'project';
  }

  const validTargets = ['auto', 'global', 'project', 'claude', 'codex', 'gemini', 'both', 'all'];
  if (!validTargets.includes(target)) {
    throw new Error(`Invalid --target "${target}". Use auto|global|project|claude|codex|gemini|both|all.`);
  }

  return { target };
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);

  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    const files = fs.readdirSync(src);
    for (const file of files) {
      copyRecursive(path.join(src, file), path.join(dest, file));
    }
  } else {
    fs.copyFileSync(src, dest);
    if (src.endsWith('.sh') || src.endsWith('.py')) {
      fs.chmodSync(dest, 0o755);
    }
  }
}

function commandExists(command) {
  try {
    const checkCmd = process.platform === 'win32' ? `where ${command}` : `command -v ${command}`;
    execSync(checkCmd, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

try {
  const { target: requestedTarget } = parseArgs(process.argv);

  const homeDir = process.env.HOME || process.env.USERPROFILE;
  const skillsSrc = path.join(packageRoot, 'plugins', 'deep-research', 'skills', 'deep-research');

  if (!fs.existsSync(skillsSrc)) {
    throw new Error(`Skills source not found: ${skillsSrc}`);
  }

  // Define CLI configurations
  const cliConfigs = {
    claude: {
      name: 'Claude Code',
      globalDir: path.join(homeDir, '.claude'),
      projectDir: path.join(targetDir, '.claude'),
      command: 'claude'
    },
    codex: {
      name: 'Codex CLI',
      globalDir: path.join(homeDir, '.codex'),
      projectDir: path.join(targetDir, '.codex'),
      command: 'codex'
    },
    gemini: {
      name: 'Gemini CLI',
      globalDir: path.join(homeDir, '.gemini'),
      projectDir: path.join(targetDir, '.gemini'),
      command: 'gemini'
    }
  };

  // Determine which CLIs to install for
  let targetClis = [];

  if (requestedTarget === 'auto') {
    // Auto-detect available CLIs
    for (const [key, config] of Object.entries(cliConfigs)) {
      if (commandExists(config.command) || fs.existsSync(config.globalDir) || fs.existsSync(config.projectDir)) {
        targetClis.push(key);
      }
    }
    if (targetClis.length === 0) {
      targetClis = ['claude']; // Default to claude
    }
    console.log(`${CYAN}Auto-detected CLIs:${NC} ${targetClis.join(', ')}`);
    console.log();
  } else if (requestedTarget === 'both') {
    targetClis = ['claude', 'codex'];
  } else if (requestedTarget === 'all') {
    targetClis = ['claude', 'codex', 'gemini'];
  } else if (requestedTarget === 'global' || requestedTarget === 'project') {
    targetClis = ['claude']; // Default to claude for global/project
  } else {
    targetClis = [requestedTarget]; // Single CLI specified
  }

  // Determine if global or project install
  const isGlobal = requestedTarget === 'global' ||
    ['claude', 'codex', 'gemini', 'both', 'all'].includes(requestedTarget) ||
    (requestedTarget === 'auto' && !fs.existsSync(path.join(targetDir, '.claude')));

  let totalFiles = 0;
  const installed = [];

  for (const cli of targetClis) {
    const config = cliConfigs[cli];
    const cliDir = isGlobal ? config.globalDir : config.projectDir;
    const skillsDest = path.join(cliDir, 'skills', 'deep-research');
    const displayPath = isGlobal
      ? `~/.${cli}/skills/deep-research`
      : `.${cli}/skills/deep-research`;

    // Create directory if needed
    if (!fs.existsSync(cliDir)) {
      fs.mkdirSync(cliDir, { recursive: true });
    }

    console.log(`${YELLOW}Installing for ${config.name}...${NC}`);
    copyRecursive(skillsSrc, skillsDest);
    console.log(`${GREEN}  ✓ ${displayPath}${NC}`);

    // Count files
    let fileCount = 0;
    function countFiles(dir) {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        if (fs.statSync(fullPath).isDirectory()) {
          countFiles(fullPath);
        } else {
          fileCount++;
        }
      }
    }
    countFiles(skillsDest);
    totalFiles += fileCount;
    installed.push({ cli, displayPath, fileCount });
  }

  console.log();
  console.log(`${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
  console.log(`${GREEN}  Installation complete! (${totalFiles} files total)${NC}`);
  console.log(`${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}`);
  console.log();
  console.log(`${CYAN}Installed to:${NC}`);
  for (const { cli, displayPath } of installed) {
    console.log(`  ${displayPath}`);
  }
  console.log();
  console.log(`${CYAN}Usage:${NC}`);
  console.log(`  /deep-research [topic]`);
  console.log(`  "딥리서치 [주제]"`);
  console.log(`  "[주제]에 대해 리서치해줘"`);
  console.log();
  console.log(`${YELLOW}Note: Restart your CLI to load the new skill.${NC}`);

} catch (error) {
  console.error(`${RED}Error during installation: ${error.message}${NC}`);
  process.exit(1);
}
