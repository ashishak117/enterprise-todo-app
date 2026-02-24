import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [todos, setTodos] = useState([])
  const [title, setTitle] = useState('')

  // Backend URL
  const API_URL = "http://54.211.230.19:8000"

  useEffect(() => {
    fetchTodos()
  }, [])

  const fetchTodos = async () => {
    try {
      const response = await axios.get(`${API_URL}/todos`)
      setTodos(response.data)
    } catch (error) {
      console.error("Error fetching todos:", error)
    }
  }

  const addTodo = async (e) => {
    // Prevent page reload if called from form submit
    if (e) e.preventDefault()
    
    if (!title.trim()) return

    try {
      await axios.post(`${API_URL}/todos`, { title, is_completed: false })
      setTitle('')
      fetchTodos()
    } catch (error) {
      console.error("Error adding todo:", error)
    }
  }

  const deleteTodo = async (id) => {
    try {
      await axios.delete(`${API_URL}/todos/${id}`)
      fetchTodos()
    } catch (error) {
      console.error("Error deleting todo:", error)
    }
  }

  return (
    <div className="app-wrapper">
      <div className="app-container">
        <header className="app-header">
          <h1>🚀 Enterprise Tasks</h1>
          <p className="subtitle">Manage your aws infrastructure</p>
        </header>

        <form className="input-group" onSubmit={addTodo}>
          <input 
            type="text" 
            value={title} 
            onChange={(e) => setTitle(e.target.value)} 
            placeholder="Add a new task..."
          />
          <button type="submit" className="add-btn">
            <span>+</span>
          </button>
        </form>

        <div className="todo-list">
          {todos.length === 0 ? (
            <div className="empty-state">
              <p>No tasksss yet. Time to build something!</p>
            </div>
          ) : (
            todos.map(todo => (
              <div key={todo.id} className="todo-card">
                <div className="todo-content">
                  <div className={`status-indicator ${todo.is_completed ? 'completed' : 'pending'}`}></div>
                  <span className="todo-title">{todo.title}</span>
                </div>
                <button onClick={() => deleteTodo(todo.id)} className="delete-btn" title="Delete Task">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default App