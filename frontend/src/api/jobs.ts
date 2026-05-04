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
