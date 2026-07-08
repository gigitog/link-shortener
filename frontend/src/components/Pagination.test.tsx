import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Pagination } from './Pagination'

describe('Pagination', () => {
  it('на первой странице кнопка "Zurück" неактивна, "Weiter" — активна', () => {
    render(<Pagination page={1} total={28} limit={10} onPageChange={vi.fn()} />)

    expect(screen.getByText('Zurück')).toBeDisabled()
    expect(screen.getByText('Weiter')).toBeEnabled()
    // total=28, limit=10 → 3 страницы (Math.ceil(28/10))
    expect(screen.getByText('Seite 1 von 3')).toBeInTheDocument()
  })

  it('на последней странице "Weiter" неактивна, "Zurück" — активна', () => {
    render(<Pagination page={3} total={28} limit={10} onPageChange={vi.fn()} />)

    expect(screen.getByText('Zurück')).toBeEnabled()
    expect(screen.getByText('Weiter')).toBeDisabled()
  })

  it('пустой список (total=0) показывает "Seite 1 von 1", а не "von 0"', () => {
    render(<Pagination page={1} total={0} limit={10} onPageChange={vi.fn()} />)

    expect(screen.getByText('Seite 1 von 1')).toBeInTheDocument()
  })

  it('клик по "Weiter"/"Zurück" вызывает onPageChange с соседней страницей', async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()
    render(<Pagination page={2} total={28} limit={10} onPageChange={onPageChange} />)

    await user.click(screen.getByText('Weiter'))
    expect(onPageChange).toHaveBeenCalledWith(3)

    await user.click(screen.getByText('Zurück'))
    expect(onPageChange).toHaveBeenCalledWith(1)
  })
})
