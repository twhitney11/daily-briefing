// Keep an unavailable illustration and its caption out of the reading flow.
document.querySelectorAll('figure img').forEach((image) => {
  const omit = () => { image.closest('figure').hidden = true; };
  image.addEventListener('error', omit, { once: true });
  if (image.complete && image.naturalWidth === 0) omit();
});
