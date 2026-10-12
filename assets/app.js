const searchInput = document.querySelector("#catalog-search");
const filters = [...document.querySelectorAll(".filter")];
const cards = [...document.querySelectorAll(".resource-card")];
const emptyState = document.querySelector("#empty-state");

let activeFilter = "all";

function applyCatalogFilter() {
  const query = searchInput.value.trim().toLocaleLowerCase("ko-KR");
  let visibleCount = 0;

  cards.forEach((card) => {
    const typeMatches = activeFilter === "all" || card.dataset.type === activeFilter;
    const textMatches = !query || card.dataset.search.toLocaleLowerCase("ko-KR").includes(query) || card.textContent.toLocaleLowerCase("ko-KR").includes(query);
    const isVisible = typeMatches && textMatches;
    card.hidden = !isVisible;
    if (isVisible) visibleCount += 1;
  });

  emptyState.hidden = visibleCount !== 0;
}

filters.forEach((filter) => {
  filter.addEventListener("click", () => {
    activeFilter = filter.dataset.filter;
    filters.forEach((item) => {
      const isActive = item === filter;
      item.classList.toggle("is-active", isActive);
      item.setAttribute("aria-pressed", String(isActive));
    });
    applyCatalogFilter();
  });
});

searchInput.addEventListener("input", applyCatalogFilter);
