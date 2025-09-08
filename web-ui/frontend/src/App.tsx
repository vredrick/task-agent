import { Routes, Route } from 'react-router-dom'
import AgentSelection from './pages/AgentSelection'
import Chat from './pages/Chat'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<AgentSelection />} />
        <Route path="/chat/:agentName" element={<Chat />} />
      </Routes>
    </div>
  )
}

export default App