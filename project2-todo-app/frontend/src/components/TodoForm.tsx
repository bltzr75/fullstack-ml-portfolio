import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { CreateTodoRequest } from '../types/todo';
import { RootState, AppDispatch } from '../store/store';
import { createTodo, setError } from '../store/todoSlice';

const TodoForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { error } = useSelector((state: RootState) => state.todos);
  const [formData, setFormData] = useState<CreateTodoRequest>({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
  });
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleChange = (field: keyof CreateTodoRequest) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    
    // Clear form error when user starts typing
    if (formError) {
      setFormError(null);
    }
    
    // Clear global error when user interacts with form
    if (error) {
      dispatch(setError(null));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!formData.title.trim()) {
      setFormError('Title is required');
      return;
    }

    setLoading(true);
    setFormError(null);

    try {
      await dispatch(createTodo({
        ...formData,
        description: formData.description || undefined,
        dueDate: formData.dueDate || undefined,
      }));
      
      // Reset form only on success
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        dueDate: '',
      });
      
    } catch (err) {
      setFormError('Failed to create todo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        Add New Todo
      </Typography>
      
      {(formError || error) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {formError || error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Title"
          value={formData.title}
          onChange={handleChange('title')}
          required
          margin="normal"
          disabled={loading}
          error={!!formError && !formData.title.trim()}
          helperText={formError && !formData.title.trim() ? 'Title is required' : ''}
        />
        
        <TextField
          fullWidth
          label="Description"
          value={formData.description}
          onChange={handleChange('description')}
          multiline
          rows={2}
          margin="normal"
          disabled={loading}
          placeholder="Optional description..."
        />
        
        <FormControl fullWidth margin="normal" disabled={loading}>
          <InputLabel>Priority</InputLabel>
          <Select
            value={formData.priority}
            label="Priority"
            onChange={handleChange('priority')}
          >
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
          </Select>
        </FormControl>
        
        <TextField
          fullWidth
          label="Due Date"
          type="date"
          value={formData.dueDate}
          onChange={handleChange('dueDate')}
          InputLabelProps={{
            shrink: true,
          }}
          margin="normal"
          disabled={loading}
          helperText="Optional due date"
        />
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !formData.title.trim()}
            sx={{ minWidth: 120 }}
          >
            {loading ? 'Adding...' : 'Add Todo'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default TodoForm;
