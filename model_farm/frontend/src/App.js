import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import TodoView from './components/TodoListView';

function App() {

  const [todoList, setTodoList] = useState([{}])
  const [title, setTitle] = useState('')
  const [description, setDesc] = useState('')

  // Read all todos
  useEffect(() => {
    axios.get("http://localhost:8000/api/todo").then(res => {
      setTodoList(res.data)
    })
  });

  // Post a todo
  const addTodoHandler = () => {
    axios.post("http://localhost:8000/api/todo", { "title": title, "description": description })
    .then(res => console.log(res))
  };

  return (
    <div className="App list-group-item justify-content-center align-item-center mx-auto" style={{ "width": "400px" }}>
      <h1 className="card text-white bg-primary mb-1">Task Manager</h1>
      <h6 className="card text-white bg-primary">FASTAPI - React - MongoDB</h6>
      <div className='card-body'>
        <h5 className='card text-white bg-dark'>Add your task</h5>
        <span className='card-text'>
          <input className="mb-2 form-control titleIn" onChange={event => setTitle(event.target.value)} placeholder='Title' />
          <input className='mb-2 form-control desIn' onChange={event => setDesc(event.target.value)} placeholder='Description' />
          <button className='btn btn-outline-primary mb-5 mx-2' style={{'borderRadius': '50px', "font-weight": "bold"}} onClick={addTodoHandler}>Add Task</button>
        </span>
        <h5 className='card mb-2'>Your Tasks</h5>
        <div>
          <TodoView todoList={todoList}/>
        </div>
      </div>
    </div>
  );
}

export default App;
