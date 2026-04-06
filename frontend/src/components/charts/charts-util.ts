// helper functions with gpt-5.4

export function formatChartDate(date: Date | string) {
  const parsedDate = date instanceof Date ? date : new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(parsedDate);
}

export function formatChartDateRange(
  startDate?: Date | string,
  endDate?: Date | string,
) {
  const formattedStartDate = startDate ? formatChartDate(startDate) : null;
  const formattedEndDate = endDate ? formatChartDate(endDate) : null;

  if (formattedStartDate && formattedEndDate) {
    return `${formattedStartDate} - ${formattedEndDate}`;
  }

  return formattedStartDate ?? formattedEndDate;
}
