import path from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

/**
 * Upload flow and its error message, exercised through the Docs screen
 * (`/docs`), per the ticket's AC: "uploads a supported file through the Docs
 * screen and asserts it appears in the list, and uploads an unsupported file
 * and asserts the inline unsupported-format error is shown".
 *
 * Reuses the same tiny fixtures the backend pytest suite uses, so both
 * suites exercise the same bytes rather than drifting apart.
 */

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "backend", "tests", "fixtures");

const SUPPORTED_FILE = path.join(FIXTURES_DIR, "tiny.txt");
const UNSUPPORTED_FILE = path.join(FIXTURES_DIR, "unsupported.exe");

test.describe("document upload", () => {
  test("a supported file uploads and appears in the document list", async ({ page }) => {
    await page.goto("/docs");

    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached();
    await fileInput.setInputFiles(SUPPORTED_FILE);

    // The filename shows up somewhere in the document list once the upload
    // request resolves; poll instead of a fixed sleep since processing may
    // be asynchronous.
    await expect(page.getByText("tiny.txt")).toBeVisible({ timeout: 15_000 });
  });

  test("an unsupported file shows an inline unsupported-format error", async ({ page }) => {
    await page.goto("/docs");

    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached();
    await fileInput.setInputFiles(UNSUPPORTED_FILE);

    const error = page.getByText(/pdf.*txt.*docx|unsupported/i);
    await expect(error).toBeVisible({ timeout: 10_000 });

    // The rejected file must not appear as if it had been accepted.
    await expect(page.getByText("unsupported.exe")).not.toBeVisible();
  });
});
