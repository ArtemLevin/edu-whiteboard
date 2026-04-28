const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export type Exercise = {
  id: string
  title: string
  content: string
  subject: string
  topic: string
  difficulty: string
  answer: string | null
}

export type Attempt = {
  id: string
  user_id: string
  exercise_id: string
  board_state: Record<string, unknown>
  status: 'draft' | 'submitted' | 'checked'
  teacher_comment: string | null
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API error ${response.status}: ${text}`)
  }

  return response.json() as Promise<T>
}

export async function listExercises(): Promise<Exercise[]> {
  return request<Exercise[]>('/exercises')
}

export async function createAttempt(userId: string, exerciseId: string): Promise<Attempt> {
  return request<Attempt>('/attempts', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, exercise_id: exerciseId }),
  })
}

export async function saveBoard(attemptId: string, boardState: Record<string, unknown>): Promise<Attempt> {
  return request<Attempt>(`/attempts/${attemptId}/board`, {
    method: 'PATCH',
    body: JSON.stringify({ board_state: boardState }),
  })
}

export async function submitAttempt(attemptId: string): Promise<Attempt> {
  return request<Attempt>(`/attempts/${attemptId}/submit`, {
    method: 'POST',
  })
}
