/**
 * 日期格式化工具函数
 */

/**
 * 格式化日期为相对时间（如：刚刚、5分钟前、2小时前）
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  const diffInSeconds = Math.floor((now.getTime() - targetDate.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return '刚刚';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}小时前`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays}天前`;
  }

  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks}周前`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths}个月前`;
  }

  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears}年前`;
}

/**
 * 格式化日期为标准格式（YYYY-MM-DD HH:mm:ss）
 */
export function formatDateTime(date: string | Date): string {
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  
  const year = targetDate.getFullYear();
  const month = String(targetDate.getMonth() + 1).padStart(2, '0');
  const day = String(targetDate.getDate()).padStart(2, '0');
  const hours = String(targetDate.getHours()).padStart(2, '0');
  const minutes = String(targetDate.getMinutes()).padStart(2, '0');
  const seconds = String(targetDate.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 格式化日期为日期格式（YYYY-MM-DD）
 */
export function formatDate(date: string | Date): string {
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  
  const year = targetDate.getFullYear();
  const month = String(targetDate.getMonth() + 1).padStart(2, '0');
  const day = String(targetDate.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}

/**
 * 格式化日期为时间格式（HH:mm:ss）
 */
export function formatTime(date: string | Date): string {
  const targetDate = typeof date === 'string' ? new Date(date) : date;
  
  const hours = String(targetDate.getHours()).padStart(2, '0');
  const minutes = String(targetDate.getMinutes()).padStart(2, '0');
  const seconds = String(targetDate.getSeconds()).padStart(2, '0');

  return `${hours}:${minutes}:${seconds}`;
}

/**
 * 文本截断工具函数
 */

/**
 * 截断文本到指定长度，并添加省略号
 */
export function truncateText(text: string, maxLength: number, ellipsis = '...'): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength - ellipsis.length) + ellipsis;
}

/**
 * 按单词边界截断文本（避免截断单词中间）
 */
export function truncateTextByWord(text: string, maxLength: number, ellipsis = '...'): string {
  if (text.length <= maxLength) {
    return text;
  }

  const truncated = text.slice(0, maxLength - ellipsis.length);
  const lastSpaceIndex = truncated.lastIndexOf(' ');

  if (lastSpaceIndex > 0) {
    return truncated.slice(0, lastSpaceIndex) + ellipsis;
  }

  return truncated + ellipsis;
}

/**
 * 截断文本到指定行数
 */
export function truncateTextByLines(text: string, maxLines: number, ellipsis = '...'): string {
  const lines = text.split('\n');
  
  if (lines.length <= maxLines) {
    return text;
  }

  return lines.slice(0, maxLines).join('\n') + ellipsis;
}
