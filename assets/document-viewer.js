const siteRoot = new URL("./", window.location.href);
const viewerUrl = new URL("document-viewer-2.html", siteRoot);
const content = document.querySelector("#document-content");
const status = document.querySelector("#document-status");

function isLocalMarkdown(url) {
  return url.origin === siteRoot.origin && url.pathname.startsWith(siteRoot.pathname) && /\.md$/i.test(url.pathname);
}

function documentViewerLink(url) {
  const target = new URL(viewerUrl);
  target.searchParams.set("doc", decodeURIComponent(url.pathname.slice(siteRoot.pathname.length)));
  target.hash = url.hash;
  return target.href;
}

function addHeadingsAndToc() {
  const usedIds = new Set();
  const links = document.querySelector("#toc-links");
  content.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((heading) => {
    const base = heading.textContent.trim().toLowerCase().replace(/[^\p{L}\p{N}\p{M}_\-\s]/gu, "").replace(/\s/g, "-") || "section";
    let id = base;
    let suffix = 0;
    while (usedIds.has(id)) id = `${base}-${++suffix}`;
    usedIds.add(id);
    heading.id = id;
    heading.tabIndex = -1;
    if (heading.tagName === "H1") return;
    const item = document.createElement("li");
    item.dataset.level = heading.tagName.slice(1);
    const link = document.createElement("a");
    link.href = `#${encodeURIComponent(id)}`;
    link.textContent = heading.textContent;
    item.append(link);
    links.append(item);
  });
  document.querySelector("#document-toc").hidden = links.children.length === 0;
}

function resolveDocumentLinks(documentUrl) {
  content.querySelectorAll("a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    if (href.startsWith("#")) return;
    const url = new URL(href, documentUrl);
    link.href = isLocalMarkdown(url) ? documentViewerLink(url) : url.href;
    if (url.origin !== siteRoot.origin && /^https?:$/.test(url.protocol)) link.rel = "noopener noreferrer";
  });
  content.querySelectorAll("img[src]").forEach((image) => {
    image.src = new URL(image.getAttribute("src"), documentUrl).href;
    image.loading = "lazy";
  });
  content.querySelectorAll("table").forEach((table) => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-scroll";
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", "표, 가로로 스크롤할 수 있다");
    table.replaceWith(wrapper);
    wrapper.append(table);
  });
}

function navigateToHeading() {
  if (!window.location.hash) return;
  try {
    const heading = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (heading && content.contains(heading)) {
      heading.scrollIntoView();
      heading.focus({ preventScroll: true });
    }
  } catch {
    // 잘못 인코딩된 앵커는 문서 읽기를 방해하지 않는다.
  }
}

async function loadDocument() {
  try {
    const path = new URLSearchParams(window.location.search).get("doc") || "개발-지침과-팁-1.md";
    const documentUrl = new URL(path, siteRoot);
    if (!isLocalMarkdown(documentUrl) || documentUrl.search || documentUrl.hash) {
      throw new Error("이 저장소 안의 마크다운 문서 경로를 지정해야 한다.");
    }
    document.querySelector("#source-link").href = documentUrl.href;
    document.querySelector("#document-path").textContent = decodeURIComponent(documentUrl.pathname.slice(siteRoot.pathname.length));
    const response = await fetch(documentUrl, { cache: "no-store" });
    if (!response.ok) throw new Error(`문서 파일을 찾거나 불러올 수 없다. (HTTP ${response.status})`);
    const markdown = await response.text();
    content.replaceChildren(DOMPurify.sanitize(marked.parse(markdown, { gfm: true }), {
      USE_PROFILES: { html: true },
      FORBID_TAGS: ["style", "form", "button", "textarea", "select"],
      FORBID_ATTR: ["style", "srcset"],
      RETURN_DOM_FRAGMENT: true,
    }));
    content.querySelectorAll("input").forEach((input) => {
      if (input.type === "checkbox") input.disabled = true;
      else input.remove();
    });
    resolveDocumentLinks(documentUrl);
    addHeadingsAndToc();
    document.title = `${content.querySelector("h1")?.textContent || "문서 읽기"} | CodingAgentHarness`;
    status.hidden = true;
    navigateToHeading();
  } catch (error) {
    content.replaceChildren();
    status.textContent = `${error.message} 자료 목록으로 돌아가 문서를 다시 선택한다.`;
    status.classList.add("document-error");
  } finally {
    content.setAttribute("aria-busy", "false");
  }
}

window.addEventListener("hashchange", navigateToHeading);
loadDocument();
