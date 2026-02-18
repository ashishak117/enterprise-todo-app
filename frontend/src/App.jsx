import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [todos, setTodos] = useState([])
  const [title, setTitle] = useState('')

  // Point to our Backend
  // NOTE: In Production, this will be an Environment Variable!
  const API_URL = "http://127.0.0.1:8000"

  useEffect(() => {
    fetchTodos()
  }, [])

  const fetchTodos = async () => {
    const response = await axios.get(`${API_URL}/todos`)
    setTodos(response.data)
  }

  const addTodo = async () => {
    if (!title) return
    await axios.post(`${API_URL}/todos`, { title, is_completed: false })
    setTitle('')
    fetchTodos()
  }

  const deleteTodo = async (id) => {
    await axios.delete(`${API_URL}/todos/${id}`)
    fetchTodos()
  }

  return (
    <div className="app-container">
      <h1>🚀 Enterprise ToDo App</h1>
      <div className="input-group">
        <input 
          type="text" 
          value={title} 
          onChange={(e) => setTitle(e.target.value)} 
          placeholder="What needs to be done?"
        />
        <button onClick={addTodo}>Add</button>
      </div>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <span>{todo.title}</span>
            <button onClick={() => deleteTodo(todo.id)}>❌</button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App