export default function HomePage() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>AutoPivot UI</h1>
      <p>Frontend is running and connected to the backend API at <code>{process.env.NEXT_PUBLIC_API_URL}</code>.</p>
      <ul>
        <li><a href="http://localhost:8000">API Gateway</a></li>
        <li><a href="http://localhost:3000">This UI</a></li>
      </ul>
    </main>
  )
}
