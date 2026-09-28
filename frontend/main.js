const container = document.getElementById('markdown-content');

async function renderMarkdown() {
  const response = await fetch('../abc.md');

  if (!response.ok) {
    throw new Error(`Failed to load abc.md (${response.status})`);
  }

  const markdown = await response.text();
  container.textContent = markdown;
}

renderMarkdown().catch((error) => {
  container.textContent = 'Unable to load markdown content.';
  console.error(error);
});
