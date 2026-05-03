import { requestJson } from './client'

export interface Job {
  id: string
  title: string
  company?: string
  jdText?: string
  createdAt: string
}

export interface CreateJobPayload {
  title: string
  company?: string
  jdText?: string
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
