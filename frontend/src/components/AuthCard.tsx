import type { ReactNode } from 'react'

// The centered card that Login and Register share.
export function AuthCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow">
        <h1 className="mb-6 text-2xl font-semibold">{title}</h1>
        {children}
      </div>
    </main>
  )
}
