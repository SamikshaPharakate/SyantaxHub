const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

console.log('\x1b[36m%s\x1b[0m', '==================================================');
console.log('\x1b[36m%s\x1b[0m', '   Starting SyntaxHub Full-Stack Environment...   ');
console.log('\x1b[36m%s\x1b[0m', '==================================================');

const isWin = os.platform() === 'win32';
const npmCmd = isWin ? 'npm.cmd' : 'npm';
const pythonCmd = isWin
  ? path.join(__dirname, 'services', '.venv', 'Scripts', 'python.exe')
  : path.join(__dirname, 'services', '.venv', 'bin', 'python');

function runProcess(name, command, args, cwd, colorCode) {
  const proc = spawn(command, args, {
    cwd,
    shell: isWin,
    stdio: 'pipe',
  });

  proc.stdout.on('data', (data) => {
    const lines = data.toString().trim().split('\n');
    lines.forEach((line) => {
      console.log(`\x1b[${colorCode}m[${name}]\x1b[0m ${line}`);
    });
  });

  proc.stderr.on('data', (data) => {
    const lines = data.toString().trim().split('\n');
    lines.forEach((line) => {
      console.log(`\x1b[${colorCode}m[${name} ERR]\x1b[0m ${line}`);
    });
  });

  proc.on('close', (code) => {
    console.log(`\x1b[${colorCode}m[${name}]\x1b[0m exited with code ${code}`);
  });

  return proc;
}

// 1. Python AI FastAPI microservice on Port 8000
const aiService = runProcess(
  'AI Service (8000)',
  pythonCmd,
  ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
  path.join(__dirname, 'services'),
  '35' // Magenta
);

// 2. Express Backend on Port 5000
const server = runProcess(
  'Express Server (5000)',
  npmCmd,
  ['run', 'dev'],
  path.join(__dirname, 'server'),
  '34' // Blue
);

// 3. Next.js Frontend on Port 3000
const client = runProcess(
  'Next.js Client (3000)',
  npmCmd,
  ['run', 'dev'],
  path.join(__dirname, 'client'),
  '32' // Green
);

process.on('SIGINT', () => {
  console.log('\nShutting down all services...');
  aiService.kill();
  server.kill();
  client.kill();
  process.exit(0);
});
