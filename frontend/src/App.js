import './App.css';
import axios from 'axios';
import { useState, useEffect } from 'react';

function App() {

  const [people, setPeople] = useState([]);

  useEffect(() => {
    axios.get('/api').then(res => setPeople(res.data));
  }, []);

  return people.map((p, index) =>  {
    return <p key={index}>{p.id} {p.name} {p.age}</p>
  });

}

export default App;
