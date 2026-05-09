import { apiClient } from './client'
import type { ApiResponse } from './client'

export interface JdPreviewSkill {
  name: string
  level: string
  category: string
}

export interface JdPreviewResponse {
  title: string
  category: string
  skills: JdPreviewSkill[]
  requirements: string[]
  domain_keywords: string[]
}

export interface ResumePreviewProject {
  name: string
  role: string
  highlights: string[]
}

export interface ResumePreviewEducation {
  school: string
  major: string
  degree: string
}

export interface ResumePreviewResponse {
  name: string
  skills: string[]
  projects: ResumePreviewProject[]
  education: ResumePreviewEducation[]
  experience_years: number
}

export function parseJdPreview(content: string): Promise<ApiResponse<JdPreviewResponse>> {
  return apiClient.post<JdPreviewResponse>('/jobs/parse-preview', { content })
}

export function parseResumePreview(content: string): Promise<ApiResponse<ResumePreviewResponse>> {
  return apiClient.post<ResumePreviewResponse>('/resumes/parse-preview', { content })
}
