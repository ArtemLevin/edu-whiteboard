import { useCallback, useMemo, useState } from 'react'
import { Tldraw, getSnapshot } from 'tldraw'
import { Attempt, saveBoard, submitAttempt } from '../api/client'

type Props = {
  attempt: Attempt
}

export function Whiteboard({ attempt }: Props) {
  const [status, setStatus] = useState(attempt.status)
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null)
  const [editor, setEditor] = useState<any>(null)

  const persistenceKey = useMemo(() => `attempt-${attempt.id}`, [attempt.id])

  const handleSave = useCallback(async () => {
    if (!editor) return

    // Сохраняем snapshot tldraw как JSON в Python API.
    const snapshot = getSnapshot(editor.store)
    await saveBoard(attempt.id, snapshot as unknown as Record<string, unknown>)
    setLastSavedAt(new Date().toLocaleTimeString())
  }, [attempt.id, editor])

  const handleSubmit = useCallback(async () => {
    await handleSave()
    const updated = await submitAttempt(attempt.id)
    setStatus(updated.status)
  }, [attempt.id, handleSave])

  return (
    <section className="board-shell">
      <header className="board-toolbar">
        <div>
          <strong>Доска решения</strong>
          <span className="muted">Статус: {status}</span>
        </div>
        <div className="toolbar-actions">
          {lastSavedAt && <span className="muted">Сохранено: {lastSavedAt}</span>}
          <button onClick={handleSave}>Сохранить</button>
          <button className="primary" onClick={handleSubmit}>Сдать</button>
        </div>
      </header>
      <div className="board-canvas">
        <Tldraw persistenceKey={persistenceKey} onMount={setEditor} />
      </div>
    </section>
  )
}
