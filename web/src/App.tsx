import { useQuery } from '@tanstack/react-query'

type ServerStatus = {
  status: string
  version: string
  resetDate: string
  serverResets: { next: string; frequency: string }
}

async function fetchStatus(): Promise<ServerStatus> {
  const res = await fetch('/api/status')
  if (!res.ok) throw new Error(`GET /api/status: ${res.status} ${await res.text()}`)
  return res.json()
}

export default function App() {
  const { data, error, isPending } = useQuery({ queryKey: ['status'], queryFn: fetchStatus })

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <h1 className="text-2xl font-semibold">Space Traders</h1>
      {isPending && <p className="mt-4 text-slate-400">Loading server status...</p>}
      {error && <p className="mt-4 text-red-400">{error.message}</p>}
      {data && (
        <dl className="mt-4 grid grid-cols-[max-content_1fr] gap-x-6 gap-y-1">
          <dt className="text-slate-400">Status</dt>
          <dd>{data.status}</dd>
          <dt className="text-slate-400">Version</dt>
          <dd>{data.version}</dd>
          <dt className="text-slate-400">Last reset</dt>
          <dd>{data.resetDate}</dd>
          <dt className="text-slate-400">Next reset</dt>
          <dd>{new Date(data.serverResets.next).toLocaleString()}</dd>
        </dl>
      )}
    </main>
  )
}
