import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'node:fs';

const python = process.env.PYTHON_EXEC || 'D:/InstalledApps/MiniConda/envs/pyenv/python.exe';
const edgeInstalled = process.platform === 'win32' && existsSync('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe');

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  timeout: 30_000,
  use: {
    baseURL: 'http://127.0.0.1:5174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions: edgeInstalled ? { channel: 'msedge' } : {},
  },
  projects: [{ name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1050 } } }],
  webServer: [
    { command: `"${python}" ../app.py`, url: 'http://127.0.0.1:5051/api/health', env: { HOST: '127.0.0.1', PORT: '5051', PYTHONIOENCODING: 'utf-8' }, reuseExistingServer: !process.env.CI },
    { command: 'npm.cmd run dev -- --port 5174', url: 'http://127.0.0.1:5174', env: { API_PROXY_TARGET: 'http://127.0.0.1:5051' }, reuseExistingServer: !process.env.CI },
  ],
});
