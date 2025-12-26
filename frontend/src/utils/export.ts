import type { Article } from '@/types/article';

/**
 * Export utility functions for converting articles to different formats
 */

/**
 * Convert articles to JSON format
 */
export const exportToJSON = (articles: Article[], fields: string[]): string => {
  const filteredArticles = articles.map((article) => filterFields(article, fields));
  return JSON.stringify(filteredArticles, null, 2);
};

/**
 * Convert articles to CSV format
 */
export const exportToCSV = (articles: Article[], fields: string[]): string => {
  if (articles.length === 0) {
    return '';
  }

  // Create header row
  const headers = fields.map((field) => escapeCSVValue(field));
  const headerRow = headers.join(',');

  // Create data rows
  const dataRows = articles.map((article) => {
    return fields
      .map((field) => {
        const value = getFieldValue(article, field);
        return escapeCSVValue(value);
      })
      .join(',');
  });

  return [headerRow, ...dataRows].join('\n');
};

/**
 * Convert articles to Excel format (using CSV with BOM for Excel compatibility)
 */
export const exportToExcel = (articles: Article[], fields: string[]): string => {
  // Add BOM for Excel UTF-8 compatibility
  const BOM = '\uFEFF';
  const csv = exportToCSV(articles, fields);
  return BOM + csv;
};

/**
 * Trigger file download in browser
 */
export const downloadFile = (content: string, filename: string, mimeType: string): void => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Download articles as JSON file
 */
export const downloadAsJSON = (articles: Article[], fields: string[]): void => {
  const content = exportToJSON(articles, fields);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `articles_${timestamp}.json`;
  downloadFile(content, filename, 'application/json');
};

/**
 * Download articles as CSV file
 */
export const downloadAsCSV = (articles: Article[], fields: string[]): void => {
  const content = exportToCSV(articles, fields);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `articles_${timestamp}.csv`;
  downloadFile(content, filename, 'text/csv;charset=utf-8;');
};

/**
 * Download articles as Excel file
 */
export const downloadAsExcel = (articles: Article[], fields: string[]): void => {
  const content = exportToExcel(articles, fields);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `articles_${timestamp}.csv`;
  downloadFile(content, filename, 'text/csv;charset=utf-8;');
};

/**
 * Helper: Filter article fields based on selected fields
 */
const filterFields = (article: Article, fields: string[]): Partial<Article> => {
  const filtered: any = {};
  fields.forEach((field) => {
    if (field in article) {
      filtered[field] = (article as any)[field];
    }
  });
  return filtered;
};

/**
 * Helper: Get field value from article (handles nested fields)
 */
const getFieldValue = (article: Article, field: string): string => {
  const value = (article as any)[field];

  if (value === null || value === undefined) {
    return '';
  }

  // Handle nested objects (tech_detection, content_analysis)
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }

  return String(value);
};

/**
 * Helper: Escape CSV value (handle quotes, commas, newlines)
 */
const escapeCSVValue = (value: string | number | boolean | null | undefined): string => {
  if (value === null || value === undefined) {
    return '';
  }

  const stringValue = String(value);

  // If value contains comma, quote, or newline, wrap in quotes and escape quotes
  if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }

  return stringValue;
};
