import { Routes, Route } from 'react-router-dom'
import AgentSelection from './pages/AgentSelection'
import Chat from './pages/Chat'

function App() {
  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <Routes>
        <Route path="/" element={<AgentSelection />} />
        <Route path="/chat/:agentName" element={<Chat />} />
      </Routes>
    </div>
  )
}

export default App