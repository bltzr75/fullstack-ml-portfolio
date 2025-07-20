import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Container, 
  Typography, 
  List, 
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import { RootState, AppDispatch } from '../store/store';
import { fetchTodos } from '../store/todoSlice';
import { getFilteredAndSortedTodos } from '../utils/todoUtils';
import TodoForm from './TodoForm';
import TodoFilters from './TodoFilters';
import TodoItem from './TodoItem';

const TodoList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { todos, loading, error, filter, sort } = useSelector((state: RootState) => state.todos);

  useEffect(() => {
    dispatch(fetchTodos());
  }, [dispatch]);

  // Get filtered and sorted todos
  const filteredAndSortedTodos = getFilteredAndSortedTodos(todos, filter, sort);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Todos
      </Typography>
      
      <TodoForm />
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <TodoFilters />
      
      <Paper elevation={3} sx={{ mt: 2 }}>
        {filteredAndSortedTodos.length === 0 ? (
          <Typography variant="body1" sx={{ p: 3, textAlign: 'center' }}>
            {todos.length === 0 
              ? 'No todos yet. Create your first todo using the form above!' 
              : `No ${filter} todos found.`
            }
          </Typography>
        ) : (
          <List>
            {filteredAndSortedTodos.map((todo) => (
              <TodoItem key={todo.id} todo={todo} />
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
};

export default TodoList;
