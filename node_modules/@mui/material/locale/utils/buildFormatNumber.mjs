const buildFormatNumber = locale => {
  let formatter;
  if (typeof Intl !== 'undefined' && Intl.NumberFormat) {
    try {
      formatter = new Intl.NumberFormat(locale);
    } catch {
      // fallback to String()
    }
  }
  return value => {
    if (!Number.isFinite(value)) {
      return String(value);
    }
    return formatter ? formatter.format(value) : String(value);
  };
};
export default buildFormatNumber;