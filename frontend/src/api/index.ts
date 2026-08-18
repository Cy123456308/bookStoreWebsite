import type {
  Article,
  Banner,
  Book,
  BookQuery,
  ArticleQuery,
  Category,
  ContactPayload,
  DownloadFile,
  NavItem,
  Paginated,
  SiteInfo,
} from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'
const API_ORIGIN = (() => {
  try {
    return new URL(API_BASE, window.location.origin).origin
  } catch {
    return ''
  }
})()

function resolveAssetUrl(value?: string): string | undefined {
  if (!value) return value
  if (/^(https?:)?\/\//i.test(value) || value.startsWith('data:') || value.startsWith('blob:')) {
    return value
  }
  if (!API_ORIGIN) return value
  if (value.startsWith('/')) return `${API_ORIGIN}${value}`
  return `${API_ORIGIN}/${value}`
}

function normalizeBook(book: Book): Book {
  return {
    ...book,
    cover: resolveAssetUrl(book.cover),
    sampleImages: book.sampleImages?.map((url) => resolveAssetUrl(url) ?? url),
  }
}

function normalizeArticle(article: Article): Article {
  return {
    ...article,
    cover: resolveAssetUrl(article.cover),
  }
}

function normalizeBanner(banner: Banner): Banner {
  return {
    ...banner,
    image: resolveAssetUrl(banner.image) ?? banner.image,
  }
}

function normalizeSite(site: SiteInfo): SiteInfo {
  return {
    ...site,
    logoUrl: resolveAssetUrl(site.logoUrl),
  }
}

function normalizeDownload(download: DownloadFile): DownloadFile {
  return {
    ...download,
    url: resolveAssetUrl(download.url) ?? download.url,
  }
}

function normalizePaginated<T>(data: Paginated<T>, mapItem: (item: T) => T): Paginated<T> {
  return {
    ...data,
    items: data.items.map(mapItem),
  }
}

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${url}`)
  }
  return (await res.json()) as T
}

export function fetchSite(): Promise<SiteInfo> {
  return getJSON<SiteInfo>(`${API_BASE}/site`).then(normalizeSite)
}

export function fetchBanners(): Promise<Banner[]> {
  return getJSON<Banner[]>(`${API_BASE}/banners`).then((items) => items.map(normalizeBanner))
}

export function fetchCategories(): Promise<Category[]> {
  return getJSON<Category[]>(`${API_BASE}/categories`)
}

export function fetchBooks(params?: BookQuery): Promise<Paginated<Book>> {
  const qs = new URLSearchParams()
  if (params?.category) qs.set('category', params.category)
  if (params?.onSale !== undefined) qs.set('onSale', String(params.onSale))
  if (params?.q) qs.set('q', params.q)
  if (params?.page) qs.set('page', String(params.page))
  if (params?.pageSize) qs.set('pageSize', String(params.pageSize))
  const query = qs.toString()
  return getJSON<Paginated<Book>>(`${API_BASE}/books${query ? `?${query}` : ''}`)
    .then((data) => normalizePaginated(data, normalizeBook))
}

export function fetchBook(id: string): Promise<Book> {
  return getJSON<Book>(`${API_BASE}/books/${id}`).then(normalizeBook)
}

export function fetchArticles(params?: ArticleQuery): Promise<Paginated<Article>> {
  const qs = new URLSearchParams()
  if (params?.page) qs.set('page', String(params.page))
  if (params?.pageSize) qs.set('pageSize', String(params.pageSize))
  const query = qs.toString()
  return getJSON<Paginated<Article>>(`${API_BASE}/articles${query ? `?${query}` : ''}`)
    .then((data) => normalizePaginated(data, normalizeArticle))
}

export function fetchArticle(id: string): Promise<Article> {
  return getJSON<Article>(`${API_BASE}/articles/${id}`).then(normalizeArticle)
}

export function fetchDownloads(): Promise<DownloadFile[]> {
  return getJSON<DownloadFile[]>(`${API_BASE}/downloads`).then((items) => items.map(normalizeDownload))
}

export async function submitContact(payload: ContactPayload): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    throw new Error(`Failed to submit contact: ${res.status}`)
  }
  return (await res.json()) as { ok: boolean }
}

export function fetchNav(): Promise<NavItem[]> {
  return getJSON<NavItem[]>(`${API_BASE}/nav`)
}

// --------------------------------------------------------------------------
// Admin (auth + write) — トークンは localStorage から付与
// --------------------------------------------------------------------------
function authHeaders(): Record<string, string> {
  const t = localStorage.getItem('hirogawa_admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

async function sendJSON<T>(method: string, url: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    let msg = `Request failed: ${res.status}`
    try {
      const e = await res.json()
      if (e && typeof e.error === 'string') msg = e.error
    } catch {
      // ignore parse error
    }
    throw new Error(msg)
  }
  return (await res.json()) as T
}

export function adminLogin(
  username: string,
  password: string,
): Promise<{ token: string }> {
  return sendJSON<{ token: string }>('POST', '/admin/login', { username, password })
}

export function adminLogout(token: string): Promise<void> {
  return fetch(`${API_BASE}/admin/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  }).then(() => undefined)
}

const MAX_UPLOAD_SIZE = 5 * 1024 * 1024 // 5 MB
const ALLOWED_UPLOAD_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

export function uploadImage(file: File): Promise<{ url: string }> {
  // Client-side pre-checks
  if (!ALLOWED_UPLOAD_TYPES.includes(file.type)) {
    return Promise.reject(new Error(`対応していないファイル形式です: ${file.type || 'unknown'} (PNG/JPEG/GIF/WebP のみ)`))
  }
  if (file.size > MAX_UPLOAD_SIZE) {
    return Promise.reject(new Error(`ファイルサイズが大きすぎます: ${(file.size / 1024 / 1024).toFixed(1)}MB (最大5MB)`))
  }
  if (file.size === 0) {
    return Promise.reject(new Error('ファイルが空です'))
  }

  const fd = new FormData()
  fd.append('file', file)
  return fetch(`${API_BASE}/admin/upload`, {
    method: 'POST',
    headers: authHeaders(),
    body: fd,
  }).then(async (r) => {
    if (!r.ok) {
      let msg = 'アップロードに失敗しました'
      try {
        const e = await r.json()
        if (e && typeof e.error === 'string') msg = e.error
      } catch {
        // ignore
      }
      throw new Error(msg)
    }
    const payload = (await r.json()) as { url: string }
    return { ...payload, url: resolveAssetUrl(payload.url) ?? payload.url }
  })
}

export function createBook(data: Partial<Book>): Promise<Book> {
  return sendJSON<Book>('POST', '/books', data)
}
export function updateBook(id: string, data: Partial<Book>): Promise<Book> {
  return sendJSON<Book>('PUT', `/books/${id}`, data)
}
export function deleteBook(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/books/${id}`)
}

export function createArticle(data: Partial<Article>): Promise<Article> {
  return sendJSON<Article>('POST', '/articles', data)
}
export function updateArticle(id: string, data: Partial<Article>): Promise<Article> {
  return sendJSON<Article>('PUT', `/articles/${id}`, data)
}
export function deleteArticle(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/articles/${id}`)
}

export function createCategory(data: { id?: string; name: string }): Promise<Category> {
  return sendJSON<Category>('POST', '/categories', data)
}
export function updateCategory(id: string, data: { name: string }): Promise<Category> {
  return sendJSON<Category>('PUT', `/categories/${id}`, data)
}
export function deleteCategory(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/categories/${id}`)
}

export function createBanner(data: Partial<Banner>): Promise<Banner> {
  return sendJSON<Banner>('POST', '/banners', data)
}
export function updateBanner(id: string, data: Partial<Banner>): Promise<Banner> {
  return sendJSON<Banner>('PUT', `/banners/${id}`, data)
}
export function deleteBanner(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/banners/${id}`)
}

export function createDownload(data: Partial<DownloadFile>): Promise<DownloadFile> {
  return sendJSON<DownloadFile>('POST', '/downloads', data)
}
export function updateDownload(id: string, data: Partial<DownloadFile>): Promise<DownloadFile> {
  return sendJSON<DownloadFile>('PUT', `/downloads/${id}`, data)
}
export function deleteDownload(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/downloads/${id}`)
}

export function updateSite(data: Partial<SiteInfo>): Promise<SiteInfo> {
  return sendJSON<SiteInfo>('PUT', '/site', data)
}

export function adminFetchNav(): Promise<NavItem[]> {
  return sendJSON<NavItem[]>('GET', '/admin/nav')
}
export function createNavItem(data: Partial<NavItem>): Promise<NavItem> {
  return sendJSON<NavItem>('POST', '/admin/nav', data)
}
export function updateNavItem(id: string, data: Partial<NavItem>): Promise<NavItem> {
  return sendJSON<NavItem>('PUT', `/admin/nav/${id}`, data)
}
export function deleteNavItem(id: string): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('DELETE', `/admin/nav/${id}`)
}
export function reorderNavItems(items: { id: string; order: number }[]): Promise<{ ok: boolean }> {
  return sendJSON<{ ok: boolean }>('PUT', '/admin/nav/reorder', { items })
}
