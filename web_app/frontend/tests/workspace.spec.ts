import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { mkdir } from 'node:fs/promises';
import type { TicketResult } from '../src/types/prediction';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Mô hình sẵn sàng' })).toBeVisible({ timeout: 15_000 });
});

test('initial state, validation, and all five original examples', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'Một yêu cầu. Đúng nơi xử lý.' })).toBeVisible();
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Vui lòng nhập nội dung yêu cầu hỗ trợ.')).toBeVisible();
  await page.getByLabel('Nội dung yêu cầu').fill('Please refund my order');
  await page.getByLabel('Email khách hàng').fill('not-an-email');
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Vui lòng nhập địa chỉ email hợp lệ.')).toBeVisible();
  const samples = await (await page.request.get('/api/samples?source=gradio')).json();
  for (const sample of samples.samples) {
    await page.getByRole('button', { name: new RegExp(sample.subject) }).click();
    await expect(page.getByLabel('Nội dung yêu cầu')).toHaveValue(sample.text);
    await expect(page.getByLabel('Email khách hàng')).toHaveValue(sample.sender);
  }
});

test('real model workflow, exact API output, clipboard, history and reset', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.getByRole('button', { name: /03 Chưa nhận hoàn tiền/ }).click();
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/route-ticket') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  const body = await (await responsePromise).json();
  const result = body.data as TicketResult;
  await expect(page.getByRole('heading', { name: result.routing_decision.category_vi, exact: true })).toBeVisible();
  await expect(page.getByText(result.routing_decision.target_department, { exact: true })).toBeVisible();
  await expect(page.getByRole('progressbar', { name: 'Điểm Đổi trả / Hoàn tiền' })).toHaveAttribute('aria-valuenow', String(result.routing_decision.all_class_probabilities['Return/Refund']));
  await expect(page.getByLabel('Nội dung phản hồi xác nhận')).toHaveText(result.automated_response);
  await page.getByRole('button', { name: 'Sao chép', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Đã sao chép' })).toBeVisible();
  // Windows clipboard normalizes LF to CRLF; preserve the actual response text.
  expect((await page.evaluate(() => navigator.clipboard.readText())).replace(/\r\n/g, '\n')).toBe(result.automated_response);
  await page.reload();
  await expect(page.getByRole('button', { name: result.ticket_id, exact: true })).toBeVisible();
  await page.getByRole('button', { name: result.ticket_id, exact: true }).click();
  await expect(page.getByLabel('Nội dung yêu cầu')).toHaveValue(result.customer_message);
  await expect(page.getByLabel('Nội dung phản hồi xác nhận')).toHaveText(result.automated_response);
  await page.getByRole('button', { name: 'Xóa nội dung' }).click();
  await expect(page.getByLabel('Nội dung yêu cầu')).toHaveValue('');
  await expect(page.getByRole('heading', { name: 'Một yêu cầu. Đúng nơi xử lý.' })).toBeVisible();
  await page.getByRole('button', { name: 'Xóa lịch sử' }).click();
  await expect(page.getByText('Chưa có yêu cầu nào được phân loại')).toBeVisible();
});

test('loading prevents duplicate submissions and keyboard shortcut works', async ({ page }) => {
  let requests = 0;
  await page.route('**/api/route-ticket', async route => {
    requests += 1;
    await new Promise(resolve => setTimeout(resolve, 650));
    await route.continue();
  });
  await page.getByLabel('Nội dung yêu cầu').fill('My card is blocked after entering the wrong pin.');
  await page.getByLabel('Nội dung yêu cầu').press('Control+Enter');
  await expect(page.getByRole('button', { name: 'Đang phân loại yêu cầu…' })).toBeDisabled();
  await expect(page.getByLabel('Nội dung yêu cầu')).toBeDisabled();
  await expect(page.getByText('Đang tìm đúng phòng ban…')).toBeVisible();
  await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
  expect(requests).toBe(1);
});

test('backend and network errors are visible and recoverable', async ({ page }) => {
  await page.getByLabel('Nội dung yêu cầu').fill('Please help with a refund');
  await page.route('**/api/route-ticket', route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ success: false, error: 'Mô hình tạm thời chưa sẵn sàng.' }) }));
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByRole('alert')).toContainText('Mô hình tạm thời chưa sẵn sàng.');
  await page.unroute('**/api/route-ticket');
  await page.route('**/api/route-ticket', route => route.abort('failed'));
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByRole('alert')).toContainText('Không thể kết nối máy chủ.');
  await page.unroute('**/api/route-ticket');
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
});

test('dashboard exposes four models, real matrices, five plots, and keyboard lightbox', async ({ page }) => {
  await page.getByRole('link', { name: 'Phân tích mô hình', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'So sánh mô hình' })).toBeVisible();
  await expect(page.locator('.benchmark-table tbody tr')).toHaveCount(4);
  await expect(page.locator('.benchmark-table tbody tr').first()).toContainText('97.46%');
  await page.getByRole('button', { name: 'ComplementNB', exact: true }).click();
  await expect(page.locator('.class-metrics')).toContainText('94.62%');
  await expect(page.getByRole('cell', { name: 'Thực tế Payment, dự đoán Payment: 1617 mẫu', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'LinearSVC', exact: true }).click();
  await expect(page.getByRole('cell', { name: 'Thực tế Payment, dự đoán Payment: 1592 mẫu', exact: true })).toBeVisible();
  for (const button of await page.locator('.plot-nav button').all()) {
    await button.click();
    const image = page.locator('.research-plot');
    await expect(image).toBeVisible();
    await expect.poll(() => image.evaluate((element: HTMLImageElement) => element.naturalWidth)).toBeGreaterThan(0);
  }
  await page.getByRole('button', { name: 'Phóng to biểu đồ' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('failed dashboard load can retry', async ({ page }) => {
  await page.route('**/api/dashboard-data', route => route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ success: false, error: 'Không thể tải kết quả đánh giá.' }) }));
  await page.getByRole('link', { name: 'Phân tích mô hình', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Không thể tải kết quả đánh giá.');
  await page.unroute('**/api/dashboard-data');
  await page.getByRole('button', { name: 'Thử lại' }).click();
  await expect(page.locator('.benchmark-table tbody tr')).toHaveCount(4);
});

test('responsive layout and complete workflow at mobile and tablet widths', async ({ page }) => {
  for (const width of [360, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 950 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('button', { name: /01 Thẻ bị khóa/ }).click();
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Phân tích mô hình', exact: true }).click();
  await expect(page.locator('.benchmark-table')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});

test('corrupt or blocked browser storage cannot break inference', async ({ page }) => {
  await page.evaluate(() => localStorage.setItem('ticket-router.history.v1', '{invalid'));
  await page.reload();
  await expect(page.getByText('Chưa có yêu cầu nào được phân loại')).toBeVisible();
  await page.evaluate(() => { Storage.prototype.setItem = () => { throw new DOMException('Storage is blocked', 'SecurityError'); }; });
  await page.getByLabel('Nội dung yêu cầu').fill('Please refund my order');
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('Trình duyệt không cho phép lưu lịch sử.');
});

test('desktop and mobile screenshots, help dialog and no unexpected console errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await mkdir('docs/screenshots', { recursive: true });
  await page.screenshot({ path: 'docs/screenshots/router-desktop.png', fullPage: true });
  await page.getByRole('button', { name: 'Hướng dẫn sử dụng' }).click();
  await expect(page.getByRole('dialog', { name: 'Từ tin nhắn đến phòng ban.' })).toBeVisible();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: /03 Chưa nhận hoàn tiền/ }).click();
  await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
  await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
  await page.screenshot({ path: 'docs/screenshots/router-result.png', fullPage: true });
  await page.getByRole('link', { name: 'Phân tích mô hình', exact: true }).click();
  await expect(page.locator('.research-plot')).toBeVisible();
  await expect.poll(() => page.locator('.research-plot').evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
  await page.screenshot({ path: 'docs/screenshots/analytics-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.getByRole('link', { name: 'Điều hướng yêu cầu', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Điều hướng yêu cầu.' })).toBeVisible();
  const mobileLayout = await page.evaluate(() => ({
    width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
    overflow: [...document.querySelectorAll<HTMLElement>('body *')].filter(element => element.getBoundingClientRect().right > innerWidth + 1).map(element => ({ tag: element.tagName, className: element.className, right: element.getBoundingClientRect().right })),
  }));
  expect(mobileLayout.scrollWidth, JSON.stringify(mobileLayout)).toBeLessThanOrEqual(mobileLayout.width);
  await page.screenshot({ path: 'docs/screenshots/router-mobile.png', fullPage: true });
  expect(errors).toEqual([]);
});

test('workspace and analytics meet automated WCAG accessibility checks', async ({ page }) => {
  for (const state of ['empty', 'result', 'analytics']) {
    if (state === 'result') {
      await page.getByRole('button', { name: /03 Chưa nhận hoàn tiền/ }).click();
      await page.getByRole('button', { name: 'Phân loại & điều hướng' }).click();
      await expect(page.getByText('Đã phân loại', { exact: true })).toBeVisible();
    }
    if (state === 'analytics') {
      await page.getByRole('link', { name: 'Phân tích mô hình', exact: true }).click();
      await expect(page.locator('.benchmark-table')).toBeVisible();
    }
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(results.violations, JSON.stringify(results.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => ({ target: n.target, failureSummary: n.failureSummary })) })), null, 2)).toEqual([]);
  }
});
