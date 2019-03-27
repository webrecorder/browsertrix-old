export default function validate(values) {
  const errors = {};
  const urls = values.get('urls');
  if (!urls || urls.length === 0) {
    errors.urls = 'Required';
  }
  return errors;
}