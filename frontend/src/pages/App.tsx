import { useEffect, useMemo, useState } from 'react'
import { Exercise, Attempt, createAttempt, listExercises } from '../api/client'
import { Whiteboard } from '../components/Whiteboard'

const DEMO_USER_ID = '11111111-1111-1111-1111-111111111111'

export function App() {
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [selected, setSelected] = useState<Exercise | null>(null)
  const [attempt, setAttempt] = useState<Attempt | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listExercises()
      .then(setExercises)
      .catch((err) => setError(err.message))
  }, [])

  const selectedTitle = useMemo(() => selected?.title ?? 'Выберите задание', [selected])

  async function startExercise(exercise: Exercise) {
    setSelected(exercise)
    setAttempt(null)
    try {
      const created = await createAttempt(DEMO_USER_ID, exercise.id)
      setAttempt(created)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  return (
    <main className="app-layout">
      <aside className="sidebar">
        <h1>Edu Whiteboard</h1>
        <p className="muted">Задание → доска → сохранение → сдача</p>
        <div className="exercise-list">
          {exercises.map((exercise) => (
            <button key={exercise.id} onClick={() => startExercise(exercise)}>
              <strong>{exercise.title}</strong>
              <span>{exercise.topic} · {exercise.difficulty}</span>
            </button>
          ))}
        </div>
        {error && <p className="error">{error}</p>}
      </aside>

      <section className="workspace">
        <article className="exercise-card">
          <span className="eyebrow">Текущее задание</span>
          <h2>{selectedTitle}</h2>
          {selected ? (
            <p>{selected.content}</p>
          ) : (
            <p className="muted">Выберите задание слева. Если список пустой, выполните seed.</p>
          )}
        </article>

        {attempt && <Whiteboard attempt={attempt} />}
      </section>
    </main>
  )
}
