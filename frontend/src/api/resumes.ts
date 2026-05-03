import { requestJson } from './client'

export interface Resume {
  id: string
  name: string
  content?: string
  createdAt: string
}

export interface CreateResumePayload {
  name: string
  content?: string
}

export async function fetchResumes() {
  return requestJson<Resume[]>('/resumes')
}

export async function createResume(payload: CreateResumePayload) {
  return requestJson<Resume>('/resumes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchResume(id: string) {
  return requestJson<Resume>(`/resumes/${id}`)
}
