/**
 * Format a date to a locale time string
 * @param {string|Date} date - The date to format
 * @returns {string} - The formatted date
 */
export const formatTime = (date) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleTimeString();
};

/**
 * Format a date to a locale date string
 * @param {string|Date} date - The date to format
 * @returns {string} - The formatted date
 */
export const formatDate = (date) => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString();
};
