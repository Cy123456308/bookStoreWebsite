export interface Book {
  id: string
  title: string
  author: string
  cover?: string
  price?: number
  isbn?: string
  publishDate?: string
  category: string
  description?: string
  onSale: boolean
  amazonUrl?: string
  relatedIds?: string[]
  sampleImages?: string[]
  sortWeight: number
  featured: boolean
}

export interface Category {
  id: string
  name: string
}

export interface Banner {
  id: string
  image: string
  title?: string
  link?: string
  order: number
  sortWeight: number
}

export interface Article {
  id: string
  title: string
  excerpt?: string
  cover?: string
  body?: string
  category?: string
  publishedAt: string
  sortWeight: number
  featured: boolean
}

export interface DownloadFile {
  id: string
  name: string
  url: string
  size?: string
  description?: string
  publishedAt?: string
}

export interface CompanyProfile {
  englishName?: string
  homepageUrl?: string
  address?: string
  access?: string
  established?: string
  contactOffice?: string
  representative?: string
  business?: string
}

export interface HomeSection {
  id: string
  title: string
  bookId: string
}

export interface SiteInfo {
  name: string
  intro: string
  twitterUrl?: string
  twitterText?: string
  email?: string
  address?: string
  phone?: string
  company?: CompanyProfile
  services: string[]
  clients: string[]
  homeSections: HomeSection[]
  logoUrl?: string
  businessLead?: string
  businessIntro?: string
  businessNote?: string
}

export interface ContactPayload {
  name: string
  email?: string
  phone?: string
  organization?: string
  postalCode?: string
  address?: string
  subject?: string
  message: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface NavItem {
  id: string
  label: string
  to: string
  order: number
  visible: boolean
}

export interface BookQuery {
  category?: string
  onSale?: boolean
  featured?: boolean
  q?: string
  page?: number
  pageSize?: number
}

export interface ArticleQuery {
  featured?: boolean
  page?: number
  pageSize?: number
}
