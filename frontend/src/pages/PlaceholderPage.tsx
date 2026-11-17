// Screens that arrive in later milestones; the navigation already links to them.
export function PlaceholderPage({ title, milestone }: { title: string; milestone: string }) {
  return (
    <section>
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="mt-2 text-gray-600">Coming in {milestone}.</p>
    </section>
  )
}
