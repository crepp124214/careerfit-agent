import { requestJson } from './client'

export interface Job {
  id: number
  title: string
  raw_text: string
  profile: Record<string, unknown>
  created_at: string
}

export interface CreateJobPayload {
  title: string
  raw_text: string
}

export interface CompareDimension {
  name: string
  category: string
  required_level: string
  weight: number
}

export interface CompareItem {
  job_id: number
  job_title: string
  dimensions: CompareDimension[]
}

export interface CompareResponse {
  schema_version: string
  items: CompareItem[]
}

export async function fetchJobs() {
  return requestJson<Job[]>('/jobs')
}

export async function createJob(payload: CreateJobPayload) {
  return requestJson<Job>('/jobs', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchJob(id: string) {
  return requestJson<Job>(`/jobs/${id}`)
}

export async function compareJobs(jobIds: number[]) {
  return requestJson<CompareResponse>('/jobs/compare', {
    method: 'POST',
    body: JSON.stringify({ job_ids: jobIds }),
  })
}
